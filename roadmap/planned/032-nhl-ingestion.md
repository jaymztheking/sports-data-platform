# NHL Data Ingestion

**Phase**: 4 — Expand Sports
**Story Points**: 5

## User Story
As a data engineer, I want NHL data ingested from nhl-api-py into Iceberg and Postgres so that the NHL domain has a populated bronze layer.

## Acceptance Criteria
- [ ] `src/domains/nhl/ingestion/game_stats.py` fetches game-level stats via nhl-api-py
- [ ] `src/domains/nhl/ingestion/player_stats.py` fetches player season stats
- [ ] `src/domains/nhl/ingestion/schedules.py` fetches game schedules
- [ ] All modules write to Iceberg tables partitioned by season
- [ ] `src/domains/nhl/loaders/iceberg_to_postgres.py` loads to `raw_nhl` schema
- [ ] `dags/nhl/nhl_ingestion_dag.py` orchestrates ingestion with parallel tasks
