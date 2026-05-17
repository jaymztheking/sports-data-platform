# NBA Data Ingestion

**Phase**: 4 — Expand Sports
**Story Points**: 5

## User Story
As a data engineer, I want NBA data ingested from nba_api into Iceberg and Postgres so that the NBA domain has a populated bronze layer.

## Acceptance Criteria
- [ ] `src/domains/nba/ingestion/player_stats.py` fetches player season stats via nba_api
- [ ] `src/domains/nba/ingestion/game_logs.py` fetches game-level player logs
- [ ] `src/domains/nba/ingestion/schedules.py` fetches game schedules
- [ ] All modules write to Iceberg tables partitioned by season
- [ ] `src/domains/nba/loaders/iceberg_to_postgres.py` loads to `raw_nba` schema
- [ ] `dags/nba/nba_ingestion_dag.py` orchestrates ingestion with parallel tasks
