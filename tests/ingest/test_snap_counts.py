"""Tests for snap-count ingestion (S007, feeding S016's role feature).

No network — the loader is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import snap_counts


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "pfr_player_id": ["AbC01", "DeF02"],
            "season": [2025, 2025],
            "week": [1, 1],
            "offense_pct": [0.92, 0.41],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_snap_counts", _load, raising=True)
    return captured


def test_fetch_snap_counts_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = snap_counts.fetch_snap_counts(seasons=[2025])

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [snap_counts.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_snap_counts_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    out = snap_counts.fetch_snap_counts(seasons=[2025])

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["offense_pct"].to_list() == [0.92, 0.41]


def test_fetch_snap_counts_requests_the_given_seasons(
    fake_loader: dict[str, Any],
) -> None:
    snap_counts.fetch_snap_counts(seasons=[2023, 2024])

    assert fake_loader["seasons"] == [2023, 2024]


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = snap_counts.main(["--season", "2025"])

    target = tmp_path / snap_counts.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2


def test_main_defaults_to_the_whole_history_window(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "history_start_season", 2022)
    monkeypatch.setattr(settings, "default_season", 2025)

    snap_counts.main([])

    assert fake_loader["seasons"] == [2022, 2023, 2024, 2025]
