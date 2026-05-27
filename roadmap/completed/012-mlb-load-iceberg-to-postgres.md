# MLB Bronze→Serving: Iceberg → Postgres `raw_mlb`

**Phase**: 2 — Bronze Layer
**Functional unit**: Iceberg tables → PostgreSQL `raw_mlb` schema

## User Story
As a data engineer, I want the MLB Iceberg tables read and written into the `raw_mlb` PostgreSQL schema so that dbt can transform raw data in the silver/gold layers.

## Scope
One hop: Iceberg → Postgres. Owns the loader code and the Airflow task that runs it downstream of ingestion (story 011).

## Acceptance Criteria

### Implementation
- [x] `iceberg_to_postgres.py` reads each MLB Iceberg table via Spark and writes to the `raw_mlb` Postgres schema
- [x] Supports all four tables (statcast, batting, pitching, schedules)
- [x] Idempotent load (`if_exists="replace"`)
- [x] `load_all_to_postgres()` convenience entry point
- [x] Airflow `load_to_postgres` task runs after all ingestion tasks complete

### Validation — unit / structural
- [x] loader function signatures, table list coverage, replace semantics, schema target `raw_mlb`

### Validation — k3s integration / data contract
- [x] After a load, `raw_mlb` schema contains `statcast`, `batting`, `pitching`, `schedules` tables
- [x] Postgres row counts match the source Iceberg tables (within tolerance)
- [x] Metadata columns (`ingested_at`, `source`, `season`) survive the round-trip
- [x] Re-running the load does not duplicate rows (idempotency)

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
