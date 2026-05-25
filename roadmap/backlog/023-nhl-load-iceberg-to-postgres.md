# NHL Bronze→Serving: Iceberg → Postgres `raw_nhl`

**Phase**: 4 — Expand Sports
**Functional unit**: NHL Iceberg tables → PostgreSQL `raw_nhl` schema

## User Story
As a data engineer, I want the NHL Iceberg tables loaded into the `raw_nhl` Postgres schema so that dbt can transform them.

## Scope
One hop: Iceberg → Postgres. Owns `src/domains/nhl/loaders/iceberg_to_postgres.py` and the downstream load task.

## Acceptance Criteria

### Implementation
- [ ] loader reads each NHL Iceberg table and writes to `raw_nhl`
- [ ] covers game_stats, player_stats, schedules
- [ ] idempotent (`if_exists="replace"`); `load_all_to_postgres()` entry point
- [ ] load task runs after ingestion completes

### Validation — unit / structural
- [ ] loader signatures, table coverage, replace semantics, `raw_nhl` target

### Validation — k3s integration / data contract
- [ ] `raw_nhl` contains the three tables after a load
- [ ] Postgres row counts match source Iceberg tables (within tolerance)
- [ ] metadata columns survive the round-trip; re-running does not duplicate rows

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
