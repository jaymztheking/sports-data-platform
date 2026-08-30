"""Ingest fantasy draft rankings: nflreadpy → ``<data_dir>/ff_rankings.parquet``.

Downloads current FantasyPros draft rankings (ECR + ADP) via ffverse, stamps
provenance columns (``ingested_at`` / ``source``), and writes Parquet. Full
refresh: every run re-downloads and overwrites the file.

Unlike the other ingest modules this takes **no season** — ``load_ff_rankings``
serves the current draft board only, which is the whole point: it is the market
price side of S005A's value-over-ADP calculation. Because it is a live snapshot,
re-run it close to the draft.

Every run also **appends** a dated snapshot to ``ff_rankings_snapshots.parquet``
(added 2026-08-30, S007) — ``ff_rankings.parquet`` itself stays a full-refresh
overwrite so the existing S004/S005A draft-board pipeline is untouched. There is no
vendor-side ECR history, so this is the only way S017 gets anything to backtest
ECR against, starting from whenever this first runs.

Run it with::

    python -m nfl.ingest.ff_rankings

Unit tests mock the loader — no network in CI (see tests/ingest/test_ff_rankings.py).
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime

import nflreadpy as nfl
import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, append_snapshot_parquet, write_parquet

SOURCE = "nflreadpy:ff_rankings"
FILENAME = "ff_rankings.parquet"
FILENAME_SNAPSHOTS = "ff_rankings_snapshots.parquet"


def fetch_ff_rankings() -> pl.DataFrame:
    """Return the current fantasy draft rankings with metadata columns added."""
    df = nfl.load_ff_rankings(type="draft")
    df = add_metadata(df, source=SOURCE)
    return df


def main(argv: list[str] | None = None) -> int:
    """Ingest current fantasy draft rankings and write them to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest fantasy draft rankings (ECR/ADP)")
    parser.parse_args(argv)

    df = fetch_ff_rankings()
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE}: {df.height} rows → {path}")

    today = datetime.now(UTC).date()
    snapshot_path = append_snapshot_parquet(
        df, settings.data_dir / FILENAME_SNAPSHOTS, snapshot_date=today
    )
    print(f"{SOURCE} snapshot {today}: {df.height} rows → {snapshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
