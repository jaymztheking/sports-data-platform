"""Tests for the shared ingest helpers (S003, S007)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import polars as pl

from nfl.ingest._common import add_metadata, append_snapshot_parquet, write_parquet


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


def test_append_snapshot_parquet_creates_the_file_on_first_run(tmp_path: Path) -> None:
    target = tmp_path / "history.parquet"

    written = append_snapshot_parquet(
        pl.DataFrame({"x": [1, 2]}), target, snapshot_date=dt.date(2026, 8, 30)
    )

    assert written == target
    out = pl.read_parquet(target)
    assert out["x"].to_list() == [1, 2]
    assert out["snapshot_date"].to_list() == [dt.date(2026, 8, 30)] * 2


def test_append_snapshot_parquet_keeps_prior_runs_on_a_different_date(
    tmp_path: Path,
) -> None:
    """The one behavior a live-only source needs and `write_parquet` can't give it:
    a second run must not erase the first — S017 backtests off the accumulated history."""
    target = tmp_path / "history.parquet"
    append_snapshot_parquet(pl.DataFrame({"x": [1]}), target, snapshot_date=dt.date(2026, 8, 30))

    append_snapshot_parquet(pl.DataFrame({"x": [2]}), target, snapshot_date=dt.date(2026, 8, 31))

    out = pl.read_parquet(target).sort("snapshot_date")
    assert out["snapshot_date"].to_list() == [dt.date(2026, 8, 30), dt.date(2026, 8, 31)]
    assert out["x"].to_list() == [1, 2]


def test_append_snapshot_parquet_is_idempotent_for_a_same_day_rerun(tmp_path: Path) -> None:
    """A rerun on the same date with identical rows must not double the history."""
    target = tmp_path / "history.parquet"
    append_snapshot_parquet(pl.DataFrame({"x": [1, 2]}), target, snapshot_date=dt.date(2026, 8, 30))

    append_snapshot_parquet(pl.DataFrame({"x": [1, 2]}), target, snapshot_date=dt.date(2026, 8, 30))

    out = pl.read_parquet(target)
    assert out.height == 2


def test_append_snapshot_parquet_dedupes_across_a_differing_ingested_at(
    tmp_path: Path,
) -> None:
    """The real-world shape: every call to `fetch_*` restamps `ingested_at` to
    `datetime.now()`, so two same-day reruns of an ingest module are never full-row
    identical. Deduping must ignore `ingested_at`, or every intraday rerun doubles
    the history despite `snapshot_date` being unchanged."""
    target = tmp_path / "history.parquet"
    append_snapshot_parquet(
        pl.DataFrame({"x": [1, 2], "ingested_at": [dt.datetime(2026, 8, 30, 9)] * 2}),
        target,
        snapshot_date=dt.date(2026, 8, 30),
    )

    append_snapshot_parquet(
        pl.DataFrame({"x": [1, 2], "ingested_at": [dt.datetime(2026, 8, 30, 15)] * 2}),
        target,
        snapshot_date=dt.date(2026, 8, 30),
    )

    out = pl.read_parquet(target)
    assert out.height == 2
