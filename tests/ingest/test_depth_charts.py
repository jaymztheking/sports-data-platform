"""Tests for depth-chart ingestion (S007, feeding S016's 2026-role feature).

No network — the loader is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import depth_charts


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "gsis_id": ["00-1", "00-2"],
            "season": [2026, 2026],
            "pos_rank": [1, 2],
            "pos_slot": ["WR1", "WR2"],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_depth_charts", _load, raising=True)
    return captured


def test_fetch_depth_charts_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = depth_charts.fetch_depth_charts(seasons=[2026])

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [depth_charts.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_depth_charts_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    out = depth_charts.fetch_depth_charts(seasons=[2026])

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["pos_slot"].to_list() == ["WR1", "WR2"]


def test_fetch_depth_charts_requests_the_given_seasons(
    fake_loader: dict[str, Any],
) -> None:
    depth_charts.fetch_depth_charts(seasons=[2025])

    assert fake_loader["seasons"] == [2025]


def test_main_defaults_to_the_upcoming_season_only(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Role is a snapshot of the season ahead, not a historical average — pulling
    the whole history window would mostly return rosters that no longer apply."""
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "current_season", 2026)

    depth_charts.main([])

    assert fake_loader["seasons"] == [2026]


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = depth_charts.main([])

    target = tmp_path / depth_charts.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2


def test_main_accepts_an_explicit_season_override(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    depth_charts.main(["--season", "2025"])

    assert fake_loader["seasons"] == [2025]
