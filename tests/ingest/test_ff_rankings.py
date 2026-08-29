"""Tests for fantasy draft-rankings ingestion (S003, feeding S005A's ADP join).

No network — the loader is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import ff_rankings


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "player": ["Ja'Marr Chase", "Bijan Robinson"],
            "pos": ["WR", "RB"],
            "ecr": [1.5, 2.4],
            "adp": [1.0, 3.0],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_ff_rankings", _load, raising=True)
    return captured


def test_fetch_ff_rankings_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = ff_rankings.fetch_ff_rankings()

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [ff_rankings.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_ff_rankings_requests_the_draft_board(fake_loader: dict[str, Any]) -> None:
    """``type='draft'`` is the preseason board — 'week' would be in-season rankings."""
    ff_rankings.fetch_ff_rankings()

    assert fake_loader["type"] == "draft"


def test_fetch_ff_rankings_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    out = ff_rankings.fetch_ff_rankings()

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["adp"].to_list() == [1.0, 3.0]


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = ff_rankings.main([])

    target = tmp_path / ff_rankings.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2
