# NFL Bronze→Serving: Iceberg → Postgres `raw_nfl`

**Phase**: 4 — Expand Sports
**Functional unit**: NFL Iceberg tables → PostgreSQL `raw_nfl` schema

## User Story
As a data engineer, I want the NFL Iceberg tables loaded into the `raw_nfl` Postgres schema so that dbt can transform them.

## Scope
One hop: Iceberg → Postgres. Owns `src/domains/nfl/loaders/iceberg_to_postgres.py` and the downstream load task.

## Acceptance Criteria

### Implementation
- [ ] loader reads each NFL Iceberg table and writes to `raw_nfl`
- [ ] covers play_by_play, weekly_stats, rosters, schedules
- [ ] idempotent (`if_exists="replace"`); `load_all_to_postgres()` entry point
- [ ] load task runs after ingestion completes

### Validation — unit / structural
- [ ] loader signatures, table coverage, replace semantics, `raw_nfl` target

### Validation — k3s integration / data contract
- [ ] `raw_nfl` contains the four tables after a load
- [ ] Postgres row counts match source Iceberg tables (within tolerance)
- [ ] metadata columns survive the round-trip; re-running does not duplicate rows

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
