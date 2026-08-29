"""Regenerate the committed no-network sample slice in ``data/samples/`` (S003).

CI points ``NFL_DATA_DIR`` at ``data/samples`` so dbt can build against a real-shaped
but tiny fixture. Run this after a full ingest into ``data/raw``::

    uv run python -m nfl.ingest.player_stats --season 2025
    uv run python -m nfl.ingest.schedules    --season 2025
    uv run python -m nfl.ingest.ff_rankings
    uv run python scripts/make_samples.py

Columns are kept intact — only rows are cut — so staging models see the true schema.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

RAW = Path("data/raw")
SAMPLES = Path("data/samples")

TEAMS = ("KC", "PHI")
MAX_WEEK = 4
# Redraft overall — the board a standard season-long league drafts from. The feed also
# carries dynasty/best-ball/superflex variants (see ecr_type), which we do not want.
REDRAFT_OVERALL = "ro"
TOP_N_RANKINGS = 60


def main() -> int:
    SAMPLES.mkdir(parents=True, exist_ok=True)

    ps = pl.read_parquet(RAW / "player_stats.parquet").filter(
        pl.col("team").is_in(TEAMS)
        & (pl.col("week") <= MAX_WEEK)
        & (pl.col("season_type") == "REG")
    )
    ps.write_parquet(SAMPLES / "player_stats.parquet")

    sc = pl.read_parquet(RAW / "schedules.parquet").filter(
        (pl.col("home_team").is_in(TEAMS) | pl.col("away_team").is_in(TEAMS))
        & (pl.col("week") <= MAX_WEEK)
    )
    sc.write_parquet(SAMPLES / "schedules.parquet")

    fr = (
        pl.read_parquet(RAW / "ff_rankings.parquet")
        .filter(pl.col("ecr_type") == REDRAFT_OVERALL)
        .sort("ecr")
        .head(TOP_N_RANKINGS)
    )
    fr.write_parquet(SAMPLES / "ff_rankings.parquet")

    for name, df in (("player_stats", ps), ("schedules", sc), ("ff_rankings", fr)):
        print(f"{name}: {df.height} rows x {df.width} cols")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
