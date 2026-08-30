"""Ingest ff_opportunity: nflreadpy → ``<data_dir>/ff_opportunity.parquet``.

Downloads the configured season window of nflverse's expected-fantasy-points
model output (the ``*_exp`` columns — production with TD luck stripped), stamps
provenance columns, and writes Parquet. Weekly grain — S016's
``int_player_efficiency_priors`` needs per-game expected production, not season
totals.

This is a *feature input*, not a finished ranking — S016 regresses per-player
rates toward the positional mean using ``*_exp`` as one signal among several. It
does not become the projection output itself; see S007's story for why this
differs from the "deliberately out" call on other borrowed fantasy analytics.

Run it with::

    python -m nfl.ingest.ff_opportunity                    # the whole window
    python -m nfl.ingest.ff_opportunity --season 2025      # one season

Unit tests mock the loader — no network in CI (see tests/ingest/test_ff_opportunity.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:ff_opportunity"
FILENAME = "ff_opportunity.parquet"


def fetch_ff_opportunity(seasons: list[int]) -> pl.DataFrame:
    """Return weekly expected-fantasy-points data for ``seasons`` with metadata added."""
    df = nfl.load_ff_opportunity(seasons=seasons, stat_type="weekly")
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of ff_opportunity data and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest ff_opportunity (expected points)")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=settings.default_seasons,
        help=f"season year(s) (default: {settings.default_seasons})",
    )
    args = parser.parse_args(argv)

    df = fetch_ff_opportunity(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
