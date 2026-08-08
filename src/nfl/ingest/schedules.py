"""Ingest schedules: nflreadpy → data/raw/schedules.parquet.

SCAFFOLD STUB — James writes the core here (S003). Mirrors player_stats.py: fill in
``fetch_schedules`` with the real `nflreadpy` loader + Polars transform, add the
``ingested_at`` / ``source`` metadata columns, and wire ``main`` so
``python -m nfl.ingest.schedules --season 2025`` writes
``settings.data_dir / "schedules.parquet"``.
"""

from __future__ import annotations

import polars as pl

SOURCE = "nflreadpy:schedules"


def fetch_schedules(season: int) -> pl.DataFrame:
    """Return schedules for ``season`` with metadata columns added."""
    raise NotImplementedError("TODO(James): nflreadpy fetch + transform + metadata cols")
