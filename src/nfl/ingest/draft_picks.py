"""Ingest draft picks: nflreadpy → ``<data_dir>/draft_picks.parquet``.

Downloads NFL draft history, stamps provenance columns, and writes Parquet.
Feeds S016's rookie-role feature (draft capital is what makes a rookie
projectable at all) and closes the ~15 blank rookies the draft board would
otherwise carry.

Defaults to **every draft class**, not the recent history window: a board
player's draft year can be decades back (a 15-year veteran's rookie season
predates ``history_start_season`` by a wide margin), and restricting the pull
would blank out veterans' draft capital along with genuine rookies.

Run it with::

    python -m nfl.ingest.draft_picks                    # every draft class
    python -m nfl.ingest.draft_picks --season 2026      # one draft class

Unit tests mock the loader — no network in CI (see tests/ingest/test_draft_picks.py).
"""

from __future__ import annotations

import argparse

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "nflreadpy:draft_picks"
FILENAME = "draft_picks.parquet"


def fetch_draft_picks(seasons: list[int] | bool = True) -> pl.DataFrame:
    """Return draft-pick history for ``seasons`` (default: every draft class)."""
    df = nfl.load_draft_picks(seasons=seasons)
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest draft-pick history and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest draft picks")
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=None,
        help="draft class year(s) (default: every draft class)",
    )
    args = parser.parse_args(argv)
    seasons: list[int] | bool = args.season if args.season is not None else True

    df = fetch_draft_picks(seasons)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={seasons}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
