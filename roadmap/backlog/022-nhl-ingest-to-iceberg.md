# NHL Bronze: nhl-api-py → Iceberg

**Phase**: 4 — Expand Sports
**Functional unit**: nhl-api-py → Iceberg tables in MinIO

## User Story
As a data engineer, I want NHL data pulled from nhl-api-py and written to Iceberg tables in MinIO so that the NHL bronze layer holds raw, partitioned data.

## Scope
One hop: nhl-api-py → Iceberg. Owns `src/domains/nhl/ingestion/` modules and their Airflow tasks. Reuses shared client modules from story 011.

## Acceptance Criteria

### Implementation
- [ ] `game_stats.py`, `player_stats.py`, `schedules.py` fetch via nhl-api-py and write to `iceberg.nhl.*`
- [ ] metadata columns (`ingested_at`, `source`, `season`) on every table
- [ ] all tables partitioned by season
- [ ] ingestion DAG runs the tasks in parallel

### Validation — unit / structural
- [ ] module signatures, metadata `withColumn` contract, `writeTo` targets, `partitionedBy("season")`

### Validation — k3s integration / data contract
- [ ] Iceberg catalog exposes namespace `nhl` with the three tables
- [ ] schemas contain metadata columns; tables partitioned by season in MinIO
- [ ] row counts > 0 and plausible; tables queryable via spark-sql

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
