"""Tests for the FantasyPros per-format rankings ingest (S023). No network."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import fp_rankings


def _page(scoring: str, name: str, pos: str, rank: float) -> str:
    blob = {
        "scoring": scoring,
        "last_updated": "9/06",
        "players": [
            {
                "player_name": name,
                "player_position_id": pos,
                "player_team_id": "CIN",
                "rank_ave": str(rank),
                "rank_ecr": 1,
                "rank_std": "1.0",
                "rank_min": "1",
                "rank_max": "6",
                "player_bye_week": "6",
                "player_id": 1234,
            }
        ],
    }
    return "<html>var ecrData = " + json.dumps(blob) + ";\n</html>"


@pytest.fixture
def fake_pages(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Serve a distinct board per scoring page, and record which pages were requested."""
    seen: dict[str, Any] = {"pages": []}
    boards = {
        "consensus-cheatsheets": _page("STD", "Jahmyr Gibbs", "RB", 1.41),
        "half-point-ppr-cheatsheets": _page("HALF", "Jahmyr Gibbs", "RB", 1.55),
        "ppr-cheatsheets": _page("PPR", "Ja'Marr Chase", "WR", 1.58),
    }

    def _fetch(page: str) -> dict[str, Any]:
        seen["pages"].append(page)
        import re

        return json.loads(re.search(r"var ecrData = (\{.*\});", boards[page]).group(1))  # type: ignore[union-attr]

    monkeypatch.setattr(fp_rankings, "_fetch_page", _fetch)
    return seen


def test_fetches_every_scoring_format(fake_pages: dict[str, Any]) -> None:
    """The whole point of this module: ffverse carries the PPR board only."""
    out = fp_rankings.fetch_fp_rankings()

    assert set(out["scoring_format"].to_list()) == {"standard", "half_ppr", "ppr"}
    assert sorted(fake_pages["pages"]) == sorted(fp_rankings.PAGES.values())


def test_consensus_number_one_differs_by_format(fake_pages: dict[str, Any]) -> None:
    """Standard and PPR disagree at the first pick, which is why format is in the grain."""
    out = fp_rankings.fetch_fp_rankings()

    best = {
        row["scoring_format"]: row["player_name"]
        for row in out.sort("rank_ave").group_by("scoring_format").first().to_dicts()
    }
    assert best["standard"] == "Jahmyr Gibbs"
    assert best["ppr"] == "Ja'Marr Chase"


def test_adds_metadata(fake_pages: dict[str, Any]) -> None:
    out = fp_rankings.fetch_fp_rankings()

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [fp_rankings.SOURCE] * out.height
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_rank_ave_is_numeric_not_the_ordinal(fake_pages: dict[str, Any]) -> None:
    """rank_ecr is an integer ordinal on a different scale and must not be substituted."""
    out = fp_rankings.fetch_fp_rankings()

    assert out["rank_ave"].dtype == pl.Float64
    assert "rank_ecr" not in out.columns


def test_missing_ecr_block_raises_rather_than_returning_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A layout change must fail loudly, not silently produce an empty board."""
    monkeypatch.setattr(
        fp_rankings.urllib.request, "urlopen", lambda *a, **k: pytest.fail("should not run")
    )
    monkeypatch.setattr(
        fp_rankings, "_fetch_page", lambda page: (_ for _ in ()).throw(RuntimeError("no ecrData"))
    )
    with pytest.raises(RuntimeError):
        fp_rankings.fetch_fp_rankings()


def test_main_writes_parquet(
    fake_pages: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = fp_rankings.main([])

    target = tmp_path / fp_rankings.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 3
