"""nflreadpy → Parquet ingestion (S003).

Each module pulls one nflverse dataset, stamps provenance columns
(``ingested_at`` / ``source``), and writes Parquet under ``settings.data_dir``.

Division of labor (see CLAUDE.md): this package holds the skeleton; the core
`nflreadpy` fetch + Polars transform in ``player_stats.py`` / ``schedules.py`` is
hand-written by James.
"""
