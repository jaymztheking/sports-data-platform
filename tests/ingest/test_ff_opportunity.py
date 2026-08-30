"""Tests for ff_opportunity ingestion (S007, feeding S016's efficiency-priors feature).

No network — the loader is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import ff_opportunity


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "player_id": ["00-1", "00-2"],
            "season": [2025, 2025],
            "week": [1, 1],
            "rec_yards_exp": [55.2, 30.1],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_ff_opportunity", _load, raising=True)
    return captured


def test_fetch_ff_opportunity_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = ff_opportunity.fetch_ff_opportunity(seasons=[2025])

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [ff_opportunity.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_ff_opportunity_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    out = ff_opportunity.fetch_ff_opportunity(seasons=[2025])

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["rec_yards_exp"].to_list() == [55.2, 30.1]


def test_fetch_ff_opportunity_requests_weekly_stat_type_for_the_seasons(
    fake_loader: dict[str, Any],
) -> None:
    """Weekly grain — S016 needs per-game expected production, not season totals."""
    ff_opportunity.fetch_ff_opportunity(seasons=[2023, 2024])

    assert fake_loader["seasons"] == [2023, 2024]
    assert fake_loader["stat_type"] == "weekly"


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = ff_opportunity.main(["--season", "2025"])

    target = tmp_path / ff_opportunity.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2


def test_main_defaults_to_the_whole_history_window(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "history_start_season", 2022)
    monkeypatch.setattr(settings, "default_season", 2025)

    ff_opportunity.main([])

    assert fake_loader["seasons"] == [2022, 2023, 2024, 2025]
