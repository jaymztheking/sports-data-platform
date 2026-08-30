"""Tests for PFR advanced-stats ingestion (S007, feeding S016's line-quality feature).

No network — the loader is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import pfr_advstats


def _fake_frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "pfr_id": ["AbC01", "DeF02"],
            "season": [2025, 2025],
            "team": ["KC", "BUF"],
            "ybc_att": [2.1, 1.8],
        }
    )


@pytest.fixture
def fake_loader(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _load(*args: Any, **kwargs: Any) -> pl.DataFrame:
        captured.update(kwargs)
        return _fake_frame()

    monkeypatch.setattr("nflreadpy.load_pfr_advstats", _load, raising=True)
    return captured


def test_fetch_pfr_advstats_adds_metadata(fake_loader: dict[str, Any]) -> None:
    out = pfr_advstats.fetch_pfr_advstats(seasons=[2025], stat_type="rush")

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [pfr_advstats.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_pfr_advstats_preserves_source_columns_and_rows(
    fake_loader: dict[str, Any],
) -> None:
    out = pfr_advstats.fetch_pfr_advstats(seasons=[2025], stat_type="rush")

    assert set(_fake_frame().columns) <= set(out.columns)
    assert out.height == _fake_frame().height
    assert out["ybc_att"].to_list() == [2.1, 1.8]


def test_fetch_pfr_advstats_requests_the_given_stat_type_and_seasons(
    fake_loader: dict[str, Any],
) -> None:
    pfr_advstats.fetch_pfr_advstats(seasons=[2023, 2024], stat_type="pass")

    assert fake_loader["seasons"] == [2023, 2024]
    assert fake_loader["stat_type"] == "pass"


def test_main_writes_both_stat_types_to_the_configured_data_dir(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = pfr_advstats.main(["--season", "2025"])

    assert rc == 0
    rush = tmp_path / pfr_advstats.FILENAME_RUSH
    pass_ = tmp_path / pfr_advstats.FILENAME_PASS
    assert rush.exists()
    assert pass_.exists()
    assert pl.read_parquet(rush).height == 2
    assert pl.read_parquet(pass_).height == 2


def test_main_defaults_to_the_whole_history_window(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "history_start_season", 2022)
    monkeypatch.setattr(settings, "default_season", 2025)

    pfr_advstats.main([])

    assert fake_loader["seasons"] == [2022, 2023, 2024, 2025]
