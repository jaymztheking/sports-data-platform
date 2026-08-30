"""Ingest PFR advanced stats: nflreadpy → ``<data_dir>/pfr_advstats_{rush,pass}.parquet``.

Downloads the configured season window of Pro-Football-Reference advanced stats for
both rush (``ybc_att`` — yards before contact per attempt, the free run-blocking
proxy) and pass (``pressure_pct``, ``times_blitzed``, ``pocket_time`` — the free
pass-protection proxies) blocking, stamps provenance columns, and writes two
Parquet files. Rush and pass carry mostly disjoint columns, so they land as
separate files rather than one sparse union.

Run it with::

    python -m nfl.ingest.pfr_advstats                    # the whole window
    python -m nfl.ingest.pfr_advstats --season 2025      # one season

Unit tests mock the loader — no network in CI (see tests/ingest/test_pfr_advstats.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:pfr_advstats"
FILENAME_RUSH = "pfr_advstats_rush.parquet"
FILENAME_PASS = "pfr_advstats_pass.parquet"


def fetch_pfr_advstats(seasons: list[int], stat_type: str) -> pl.DataFrame:
    """Return PFR advanced stats for ``seasons``/``stat_type`` with metadata added."""
    df = nfl.load_pfr_advstats(seasons=seasons, stat_type=stat_type, summary_level="week")
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of PFR advanced stats (rush + pass) and write Parquet."""
    parser = argparse.ArgumentParser(description="Ingest PFR advanced stats (rush + pass)")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=settings.default_seasons,
        help=f"season year(s) (default: {settings.default_seasons})",
    )
    args = parser.parse_args(argv)

    for stat_type, filename in (("rush", FILENAME_RUSH), ("pass", FILENAME_PASS)):
        df = fetch_pfr_advstats(args.season, stat_type=stat_type)
        path = write_parquet(df, settings.data_dir / filename)
        print(f"{SOURCE}:{stat_type} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
