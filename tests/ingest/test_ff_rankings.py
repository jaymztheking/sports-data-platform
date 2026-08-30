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


def test_main_also_appends_a_dated_snapshot(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """`ff_rankings.parquet` (S004/S005A's existing source) is unaffected — it stays a
    full-refresh overwrite. The snapshot is a separate, additive file (S007/S017), so
    changing it can never break the already-shipped draft board."""
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    ff_rankings.main([])

    snapshot = tmp_path / ff_rankings.FILENAME_SNAPSHOTS
    assert snapshot.exists()
    out = pl.read_parquet(snapshot)
    assert out.height == 2
    today = dt.datetime.now(dt.UTC).date()
    assert out["snapshot_date"].to_list() == [today, today]


def test_main_snapshot_survives_a_second_run_on_a_later_date(
    fake_loader: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    snapshot = tmp_path / ff_rankings.FILENAME_SNAPSHOTS
    ff_rankings.append_snapshot_parquet(
        pl.DataFrame({"player": ["Old Guy"]}), snapshot, snapshot_date=dt.date(2020, 1, 1)
    )

    ff_rankings.main([])

    out = pl.read_parquet(snapshot)
    assert dt.date(2020, 1, 1) in out["snapshot_date"].to_list()
    assert out.height == 3
