# NFL Data Ingestion

**Phase**: 4 — Expand Sports
**Story Points**: 5

## User Story
As a data engineer, I want NFL data ingested from nfl-data-py into Iceberg and Postgres so that the NFL domain has a populated bronze layer.

## Acceptance Criteria
- [ ] `src/domains/nfl/ingestion/play_by_play.py` fetches play-by-play data via nflreadpy
- [ ] `src/domains/nfl/ingestion/weekly_stats.py` fetches weekly player stats
- [ ] `src/domains/nfl/ingestion/rosters.py` fetches team rosters
- [ ] `src/domains/nfl/ingestion/schedules.py` fetches game schedules
- [ ] All modules write to Iceberg tables partitioned by season
- [ ] `src/domains/nfl/loaders/iceberg_to_postgres.py` loads to `raw_nfl` schema
- [ ] `dags/nfl/nfl_ingestion_dag.py` orchestrates ingestion with parallel tasks
