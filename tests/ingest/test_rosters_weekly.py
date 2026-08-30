"""Tests for weekly-roster ingestion (S007, sample-only for now — feeds S008).

No network — the loader is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import rosters_weekly


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "gsis_id": ["00-1", "00-2"],
            "season": [2025, 2025],
            "week": [1, 1],
            "status": ["ACT", "ACT"],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_rosters_weekly", _load, raising=True)
    return captured


def test_fetch_rosters_weekly_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = rosters_weekly.fetch_rosters_weekly(seasons=[2025])

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [rosters_weekly.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_rosters_weekly_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    out = rosters_weekly.fetch_rosters_weekly(seasons=[2025])

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["status"].to_list() == ["ACT", "ACT"]


def test_fetch_rosters_weekly_requests_the_given_seasons(
    fake_loader: dict[str, Any],
) -> None:
    rosters_weekly.fetch_rosters_weekly(seasons=[2023, 2024])

    assert fake_loader["seasons"] == [2023, 2024]


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = rosters_weekly.main(["--season", "2025"])

    target = tmp_path / rosters_weekly.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2


def test_main_defaults_to_the_whole_history_window(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "history_start_season", 2022)
    monkeypatch.setattr(settings, "default_season", 2025)

    rosters_weekly.main([])

    assert fake_loader["seasons"] == [2022, 2023, 2024, 2025]
