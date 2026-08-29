"""Tests for player-stats ingestion (S003).

No network: the ``nflreadpy`` loader is monkeypatched. Patching the attribute on
the ``nflreadpy`` module works because the implementation calls
``nflreadpy.load_player_stats(...)`` (i.e. ``import nflreadpy as nfl``); a
``from nflreadpy import load_player_stats`` would need the target
``nfl.ingest.player_stats.load_player_stats`` instead.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import player_stats


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "player_id": ["00-1", "00-2"],
            "season": [2025, 2025],
            "week": [1, 1],
            "fantasy_points": [12.3, 4.5],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Patch the loader and capture the kwargs the implementation passes it."""
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_player_stats", _load, raising=True)
    return captured


def test_fetch_player_stats_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = player_stats.fetch_player_stats(seasons=[2025])

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [player_stats.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_player_stats_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    """Ingest lands the source faithfully — shaping belongs in dbt staging."""
    out = player_stats.fetch_player_stats(seasons=[2025])

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["fantasy_points"].to_list() == [12.3, 4.5]


def test_fetch_player_stats_requests_weekly_grain_for_the_seasons(
    fake_loader: dict[str, Any],
) -> None:
    """Weekly grain is what S005A aggregates for per-game rates and consistency."""
    player_stats.fetch_player_stats(seasons=[2023, 2024])

    assert fake_loader["seasons"] == [2023, 2024]
    assert fake_loader["summary_level"] == "week"


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = player_stats.main(["--season", "2025"])

    target = tmp_path / player_stats.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2


def test_main_defaults_to_the_whole_history_window(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Bare `python -m nfl.ingest.*` pulls every season, not just the latest."""
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "history_start_season", 2022)
    monkeypatch.setattr(settings, "default_season", 2025)

    player_stats.main([])

    assert fake_loader["seasons"] == [2022, 2023, 2024, 2025]


def test_main_accepts_multiple_seasons(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    player_stats.main(["--season", "2023", "2024"])

    assert fake_loader["seasons"] == [2023, 2024]
