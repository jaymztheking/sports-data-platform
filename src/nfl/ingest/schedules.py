"""Ingest schedules: nflreadpy → ``<data_dir>/schedules.parquet``.

Downloads one season of games, stamps provenance columns (``ingested_at`` /
``source``), and writes Parquet. Full refresh: every run re-downloads the whole
season and overwrites the file.

The frame arrives as one row per game, REG and POST, carrying home/away teams,
kickoff, and — for games already played — final scores. Filtering, renaming, and
typing belong in dbt staging (S004), not here — ingest lands the source faithfully.

Run it with::

    python -m nfl.ingest.schedules --season 2025

Unit tests mock the loader — no network in CI (see tests/ingest/test_schedules.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:schedules"
FILENAME = "schedules.parquet"


def fetch_schedules(season: int) -> pl.DataFrame:
    """Return the game schedule for ``season`` with metadata columns added."""
    df = nfl.load_schedules(seasons=[season])
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest one season of schedules and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest game schedules")
    parser.add_argument(
        "--season",
        type=int,
        default=settings.default_season,
        help=f"season year (default: {settings.default_season})",
    )
    args = parser.parse_args(argv)

    df = fetch_schedules(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} season={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
