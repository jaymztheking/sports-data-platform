from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import polars as pl


def add_metadata(df: pl.DataFrame, source: str) -> pl.DataFrame:
    """Add ``ingested_at`` and ``source`` metadata columns to ``df``."""
    utc_now = datetime.now(UTC)
    return df.with_columns(
        pl.lit(utc_now).alias("ingested_at"),
        pl.lit(source).alias("source"),
    )


def write_parquet(df: pl.DataFrame, path: Path) -> Path:
    """Write ``df`` to Parquet at ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)
    return path


def append_snapshot_parquet(df: pl.DataFrame, path: Path, snapshot_date: date) -> Path:
    """Append ``df`` to the Parquet history at ``path``, stamped with ``snapshot_date``.

    Unlike ``write_parquet`` (full refresh, overwrites), this never erases a prior
    run: a source with no vendor-side history (a live ADP/ECR snapshot) has nothing
    to backtest against unless every run's rows survive. A same-day rerun with
    identical rows does not double the history — rows are deduped after concat,
    ignoring ``ingested_at``: every ``fetch_*`` call restamps it to ``datetime.now()``,
    so two same-day runs are otherwise never full-row identical.
    """
    stamped = df.with_columns(pl.lit(snapshot_date).alias("snapshot_date"))
    if path.exists():
        stamped = pl.concat([pl.read_parquet(path), stamped], how="diagonal_relaxed")
    dedupe_subset = [c for c in stamped.columns if c != "ingested_at"]
    stamped = stamped.unique(subset=dedupe_subset, maintain_order=True)
    return write_parquet(stamped, path)
