# MLB Ingestion Modules

**Phase**: 2 — Bronze Layer
**Story Points**: 5

## User Story
As a data engineer, I want Python modules that fetch MLB data from pybaseball and write it to Iceberg tables so that the bronze layer is populated with raw sports data.

## Acceptance Criteria
- [x] `statcast.py` fetches pitch-level Statcast data for a date range, writes to `iceberg.mlb.statcast`
- [x] `batting.py` fetches season batting stats, writes to `iceberg.mlb.batting`
- [x] `pitching.py` fetches season pitching stats, writes to `iceberg.mlb.pitching`
- [x] `schedules.py` fetches game schedules for all 30 MLB teams, writes to `iceberg.mlb.schedules`
- [x] All modules add `ingested_at`, `source`, and `season` metadata columns
- [x] All tables partitioned by season
- [x] Each module follows extract → standardize → Iceberg write pattern
