# MLB Iceberg-to-Postgres Loader

**Phase**: 2 — Bronze Layer
**Story Points**: 3

## User Story
As a data engineer, I want a loader that reads Iceberg tables and writes them to PostgreSQL so that dbt can transform the raw data in the silver/gold layers.

## Acceptance Criteria
- [x] `iceberg_to_postgres.py` reads each MLB Iceberg table via Spark
- [x] Converts to pandas and writes to `raw_mlb` PostgreSQL schema
- [x] Supports all 4 MLB tables (statcast, batting, pitching, schedules)
- [x] Uses `if_exists="replace"` for idempotent loads
- [x] `load_all_to_postgres()` convenience function loads all tables
