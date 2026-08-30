"""Ingest snap counts: nflreadpy → ``<data_dir>/snap_counts.parquet``.

Downloads the configured season window of per-player-week snap counts
(``offense_pct`` — the real "sees the field" measure), stamps provenance columns,
and writes Parquet.

Run it with::

    python -m nfl.ingest.snap_counts                    # the whole window
    python -m nfl.ingest.snap_counts --season 2025      # one season

Unit tests mock the loader — no network in CI (see tests/ingest/test_snap_counts.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:snap_counts"
FILENAME = "snap_counts.parquet"


def fetch_snap_counts(seasons: list[int]) -> pl.DataFrame:
    """Return per-player-week snap counts for ``seasons`` with metadata columns added."""
    df = nfl.load_snap_counts(seasons=seasons)
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of snap counts and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest snap counts")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=settings.default_seasons,
        help=f"season year(s) (default: {settings.default_seasons})",
    )
    args = parser.parse_args(argv)

    df = fetch_snap_counts(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
