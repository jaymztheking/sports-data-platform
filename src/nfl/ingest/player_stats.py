"""Ingest per-week player stats: nflreadpy → ``<data_dir>/player_stats.parquet``.

Downloads one season of per-week player stats, stamps provenance columns
(``ingested_at`` / ``source``), and writes Parquet. Full refresh: every run
re-downloads the whole season and overwrites the file.

The frame arrives as one row per player per week, all positions, both REG and
POST. Filtering, renaming, and typing belong in dbt staging (S004), not here —
ingest lands the source faithfully.

Run it with::

    python -m nfl.ingest.player_stats --season 2025

Unit tests mock the loader — no network in CI (see tests/ingest/test_player_stats.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:player_stats"
FILENAME = "player_stats.parquet"


def fetch_player_stats(season: int) -> pl.DataFrame:
    """Return per-week player stats for ``season`` with metadata columns added."""
    df = nfl.load_player_stats(seasons=[season], summary_level="week")
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest one season of per-week player stats and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest per-week player stats")
    parser.add_argument(
        "--season",
        type=int,
        default=settings.default_season,
        help=f"season year (default: {settings.default_season})",
    )
    args = parser.parse_args(argv)

    df = fetch_player_stats(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} season={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
