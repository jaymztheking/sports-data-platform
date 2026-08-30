"""Tests for draft-picks ingestion (S007, feeding S016's rookie-role feature).

No network — the loader is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import draft_picks


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "gsis_id": ["00-1", "00-2"],
            "season": [2026, 1999],
            "round": [1, 6],
            "pick": [3, 200],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_draft_picks", _load, raising=True)
    return captured


def test_fetch_draft_picks_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = draft_picks.fetch_draft_picks()

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [draft_picks.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_draft_picks_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    out = draft_picks.fetch_draft_picks()

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["round"].to_list() == [1, 6]


def test_fetch_draft_picks_defaults_to_every_draft_class(
    fake_loader: dict[str, Any],
) -> None:
    """A board player's draft year can be decades back — restricting to the recent
    history window would blank out veterans' draft capital, not just rookies."""
    draft_picks.fetch_draft_picks()

    assert fake_loader["seasons"] is True


def test_fetch_draft_picks_accepts_an_explicit_season_list(
    fake_loader: dict[str, Any],
) -> None:
    draft_picks.fetch_draft_picks(seasons=[2026])

    assert fake_loader["seasons"] == [2026]


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = draft_picks.main([])

    target = tmp_path / draft_picks.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2


def test_main_accepts_an_explicit_season_override(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    draft_picks.main(["--season", "2026"])

    assert fake_loader["seasons"] == [2026]
