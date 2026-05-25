# NBA Bronze: nba_api → Iceberg

**Phase**: 4 — Expand Sports
**Functional unit**: nba_api → Iceberg tables in MinIO

## User Story
As a data engineer, I want NBA data pulled from nba_api and written to Iceberg tables in MinIO so that the NBA bronze layer holds raw, partitioned data.

## Scope
One hop: nba_api → Iceberg. Owns `src/domains/nba/ingestion/` modules and their Airflow tasks. Reuses shared client modules from story 011.

## Acceptance Criteria

### Implementation
- [ ] `player_stats.py`, `game_logs.py`, `schedules.py` fetch via nba_api and write to `iceberg.nba.*`
- [ ] metadata columns (`ingested_at`, `source`, `season`) on every table
- [ ] all tables partitioned by season
- [ ] ingestion DAG runs the tasks in parallel

### Validation — unit / structural
- [ ] module signatures, metadata `withColumn` contract, `writeTo` targets, `partitionedBy("season")`

### Validation — k3s integration / data contract
- [ ] Iceberg catalog exposes namespace `nba` with the three tables
- [ ] schemas contain metadata columns; tables partitioned by season in MinIO
- [ ] row counts > 0 and plausible; tables queryable via spark-sql

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
