# NFL Bronze: nfl-data-py → Iceberg

**Phase**: 4 — Expand Sports
**Functional unit**: nfl-data-py / nflreadpy → Iceberg tables in MinIO

## User Story
As a data engineer, I want NFL data pulled from nfl-data-py and written to Iceberg tables in MinIO so that the NFL bronze layer holds raw, partitioned data.

## Scope
One hop: NFL source API → Iceberg. Owns the `src/domains/nfl/ingestion/` modules and the Airflow tasks that run them. Reuses the shared client modules established in story 011.

## Acceptance Criteria

### Implementation
- [ ] `play_by_play.py`, `weekly_stats.py`, `rosters.py`, `schedules.py` fetch via nflreadpy and write to `iceberg.nfl.*`
- [ ] metadata columns (`ingested_at`, `source`, `season`) on every table
- [ ] all tables partitioned by season
- [ ] ingestion DAG runs the tasks in parallel

### Validation — unit / structural
- [ ] module function signatures, metadata `withColumn` contract, `writeTo` targets, `partitionedBy("season")`

### Validation — k3s integration / data contract
- [ ] Iceberg catalog exposes namespace `nfl` with the four tables
- [ ] schemas contain the metadata columns; tables partitioned by season in MinIO
- [ ] row counts > 0 and plausible for the ingested season
- [ ] tables queryable via spark-sql

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
