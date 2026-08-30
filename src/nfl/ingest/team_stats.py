"""Ingest team stats: nflreadpy → ``<data_dir>/team_stats.parquet``.

Downloads the configured season window of per-team-week stats (pace, EPA, and
136 columns of team-level box score data), stamps provenance columns, and writes
Parquet. Weekly grain, matching player_stats — S016's ``int_team_environment``
aggregates to team-season.

Run it with::

    python -m nfl.ingest.team_stats                    # the whole window
    python -m nfl.ingest.team_stats --season 2025      # one season

Unit tests mock the loader — no network in CI (see tests/ingest/test_team_stats.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:team_stats"
FILENAME = "team_stats.parquet"


def fetch_team_stats(seasons: list[int]) -> pl.DataFrame:
    """Return per-team-week stats for ``seasons`` with metadata columns added."""
    df = nfl.load_team_stats(seasons=seasons, summary_level="week")
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the season window of team stats and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest team stats")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=settings.default_seasons,
        help=f"season year(s) (default: {settings.default_seasons})",
    )
    args = parser.parse_args(argv)

    df = fetch_team_stats(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
