"""Ingest depth charts: nflreadpy → ``<data_dir>/depth_charts.parquet``.

Downloads depth-chart role (``pos_rank``, ``pos_slot``) for the given season(s),
stamps provenance columns, and writes Parquet. Feeds S016's role feature — this
is what makes a rookie with no NFL history projectable at all.

Defaults to **``current_season`` only** (the upcoming season), not the history
window: role is a snapshot of the season ahead, not something to average across
history — pulling prior seasons would mostly return rosters that no longer apply.

Run it with::

    python -m nfl.ingest.depth_charts                    # the upcoming season
    python -m nfl.ingest.depth_charts --season 2025      # a specific season

Unit tests mock the loader — no network in CI (see tests/ingest/test_depth_charts.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:depth_charts"
FILENAME = "depth_charts.parquet"


def fetch_depth_charts(seasons: list[int]) -> pl.DataFrame:
    """Return depth-chart role for ``seasons`` with metadata columns added."""
    df = nfl.load_depth_charts(seasons=seasons)
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest the upcoming season's depth charts and write them to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest depth charts")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=[settings.current_season],
        help=f"season year(s) (default: [{settings.current_season}])",
    )
    args = parser.parse_args(argv)

    df = fetch_depth_charts(args.season)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
