"""nflreadpy → Parquet ingestion (S003).

Each module pulls one nflverse dataset, stamps provenance columns
(``ingested_at`` / ``source``), and writes Parquet under ``settings.data_dir``.
Modules land the source faithfully — filtering, renaming and typing belong in dbt
staging (S004).

- ``player_stats`` — per-week player stats, one season per run
- ``schedules``    — games (REG + POST), one season per run
- ``ff_rankings``  — current FantasyPros draft board (ECR/ADP); no season, live snapshot
"""
