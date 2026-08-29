from __future__ import annotations

from datetime import UTC, datetime
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
