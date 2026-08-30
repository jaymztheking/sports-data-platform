"""Ingest injury reports: nflreadpy → ``<data_dir>/injuries.parquet``.

Downloads the configured season window of weekly injury reports, stamps
provenance columns, and writes Parquet. Sample-only for now — no S016/S018
feature consumes this yet; it is here for S008 (usage/opportunity intermediates).

Run it with::

    python -m nfl.ingest.injuries                    # the whole window
    python -m nfl.ingest.injuries --season 2025      # one season

Unit tests mock the loader — no network in CI (see tests/ingest/test_injuries.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:injuries"
FILENAME = "injuries.parquet"


def fetch_injuries(seasons: list[int]) -> pl.DataFrame:
    """Return weekly injury reports for ``seasons`` with metadata columns added."""
    df = nfl.load_injuries(seasons=seasons)
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of injury reports and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest injury reports")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=settings.default_seasons,
        help=f"season year(s) (default: {settings.default_seasons})",
    )
    args = parser.parse_args(argv)

    df = fetch_injuries(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
