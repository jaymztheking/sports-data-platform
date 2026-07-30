"""Ingest weekly player stats: nflreadpy → data/raw/weekly.parquet.

SCAFFOLD STUB — James writes the core here (S003). Fill in ``fetch_weekly`` with
the real `nflreadpy` loader + Polars transform, add the ``ingested_at`` / ``source``
metadata columns, and wire ``main`` so ``python -m nfl.ingest.weekly --season 2025``
writes ``settings.data_dir / "weekly.parquet"``.

Unit tests must mock the loader — no network in CI (see tests/ingest/test_weekly.py).
"""

from __future__ import annotations

import polars as pl

SOURCE = "nflreadpy:weekly"


def fetch_weekly(season: int) -> pl.DataFrame:
    """Return weekly player stats for ``season`` with metadata columns added."""
    raise NotImplementedError("TODO(James): nflreadpy fetch + transform + metadata cols")
