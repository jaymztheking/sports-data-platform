"""Tests for the shared ingest helpers (S003)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import polars as pl

from nfl.ingest._common import add_metadata, write_parquet


def test_add_metadata_appends_provenance_columns() -> None:
    df = pl.DataFrame({"player_id": ["00-1", "00-2"]})

    out = add_metadata(df, source="unit:test")

    assert out.columns == ["player_id", "ingested_at", "source"]
    assert out["source"].to_list() == ["unit:test", "unit:test"]
    assert out.height == df.height


def test_add_metadata_stamps_one_utc_instant_for_the_whole_frame() -> None:
    """Every row shares a single timestamp, so a run is identifiable as one batch."""
    out = add_metadata(pl.DataFrame({"x": [1, 2, 3]}), source="unit:test")

    stamps = out["ingested_at"].unique().to_list()
    assert len(stamps) == 1
    assert stamps[0].tzinfo is not None
    assert stamps[0] <= dt.datetime.now(dt.UTC)


def test_add_metadata_does_not_mutate_the_input() -> None:
    df = pl.DataFrame({"x": [1]})

    add_metadata(df, source="unit:test")

    assert df.columns == ["x"]


def test_write_parquet_creates_parent_dirs_and_roundtrips(tmp_path: Path) -> None:
    df = pl.DataFrame({"x": [1, 2]})
    target = tmp_path / "nested" / "deeper" / "out.parquet"

    written = write_parquet(df, target)

    assert written == target
    assert target.exists()
    assert pl.read_parquet(target).equals(df)


def test_write_parquet_overwrites_existing_file(tmp_path: Path) -> None:
    """Ingest is a full refresh — a second run must replace, not append."""
    target = tmp_path / "out.parquet"
    write_parquet(pl.DataFrame({"x": [1, 2, 3]}), target)

    write_parquet(pl.DataFrame({"x": [9]}), target)

    assert pl.read_parquet(target)["x"].to_list() == [9]
