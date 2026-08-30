"""Ingest weekly rosters: nflreadpy → ``<data_dir>/rosters_weekly.parquet``.

Downloads the configured season window of per-player-week roster status, stamps
provenance columns, and writes Parquet. Sample-only for now — no S016/S018
feature consumes this yet; it is here for S008 (usage/opportunity intermediates).

Run it with::

    python -m nfl.ingest.rosters_weekly                    # the whole window
    python -m nfl.ingest.rosters_weekly --season 2025      # one season

Unit tests mock the loader — no network in CI (see tests/ingest/test_rosters_weekly.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:rosters_weekly"
FILENAME = "rosters_weekly.parquet"


def fetch_rosters_weekly(seasons: list[int]) -> pl.DataFrame:
    """Return per-player-week roster status for ``seasons`` with metadata added."""
    df = nfl.load_rosters_weekly(seasons=seasons)
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of weekly rosters and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest weekly rosters")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=settings.default_seasons,
        help=f"season year(s) (default: {settings.default_seasons})",
    )
    args = parser.parse_args(argv)

    df = fetch_rosters_weekly(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
