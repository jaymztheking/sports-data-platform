"""Ingest schedules: nflreadpy → ``<data_dir>/schedules.parquet``.

Downloads the configured season window of games, stamps provenance columns (``ingested_at`` /
``source``), and writes Parquet. Full refresh: every run re-downloads the whole
season and overwrites the file.

The frame arrives as one row per game, REG and POST, carrying home/away teams,
kickoff, and — for games already played — final scores. Filtering, renaming, and
typing belong in dbt staging (S004), not here — ingest lands the source faithfully.

Default pull is the history window **plus** ``current_season`` (added 2026-08-30 for
S016/S007): Vegas lines for the upcoming season have no history-window equivalent,
since no games in it have been played yet, so schedules diverges from the other
ingest modules and always reaches one season past the historical window.

Run it with::

    python -m nfl.ingest.schedules                    # window + upcoming season
    python -m nfl.ingest.schedules --season 2025      # one season

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


def fetch_schedules(seasons: list[int]) -> pl.DataFrame:
    """Return the game schedule for ``seasons`` with metadata columns added."""
    df = nfl.load_schedules(seasons=seasons)
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of schedules and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest game schedules")
    default_seasons = [*settings.default_seasons, settings.current_season]
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=default_seasons,
        help=f"season year(s) (default: {default_seasons})",
    )
    args = parser.parse_args(argv)

    df = fetch_schedules(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
