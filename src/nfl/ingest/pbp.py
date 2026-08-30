"""Ingest play-by-play: nflreadpy → ``<data_dir>/pbp.parquet``.

Downloads the configured season window of play-by-play (49k rows x 372 cols,
~13 MB/season — by far the largest source this platform ingests), stamps
provenance columns, and writes Parquet. Sample-only for now — no S016/S018
feature consumes this yet; it is here for S008 (usage/opportunity intermediates).

Because of the size, the committed ``data/samples/`` slice for this source must
be a couple of full games, not a token row filter — see ``scripts/make_samples.py``.

Run it with::

    python -m nfl.ingest.pbp                    # the whole window
    python -m nfl.ingest.pbp --season 2025      # one season

Unit tests mock the loader — no network in CI (see tests/ingest/test_pbp.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:pbp"
FILENAME = "pbp.parquet"


def fetch_pbp(seasons: list[int]) -> pl.DataFrame:
    """Return play-by-play for ``seasons`` with metadata columns added."""
    df = nfl.load_pbp(seasons=seasons)
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of play-by-play and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest play-by-play")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=settings.default_seasons,
        help=f"season year(s) (default: {settings.default_seasons})",
    )
    args = parser.parse_args(argv)

    df = fetch_pbp(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
