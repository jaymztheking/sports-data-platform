"""Ingest per-week player stats: nflreadpy → data/raw/player_stats.parquet.

SCAFFOLD STUB — James writes the core here (S003). Fill in ``fetch_player_stats``
with the real `nflreadpy` loader + Polars transform, add the ``ingested_at`` /
``source`` metadata columns, and wire ``main`` so
``python -m nfl.ingest.player_stats --season 2025`` writes
``settings.data_dir / "player_stats.parquet"``.

The loader is ``nflreadpy.load_player_stats(seasons=..., summary_level="week")`` —
one row per player per week, all positions and both REG/POST. Filtering and
renaming belong in dbt staging (S004), not here.

Unit tests must mock the loader — no network in CI (see
tests/ingest/test_player_stats.py).
"""

from __future__ import annotations

import polars as pl

SOURCE = "nflreadpy:player_stats"


def fetch_player_stats(season: int) -> pl.DataFrame:
    """Return per-week player stats for ``season`` with metadata columns added."""
    raise NotImplementedError("TODO(James): nflreadpy fetch + transform + metadata cols")
