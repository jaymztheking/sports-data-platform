# NBA Bronze→Serving: Iceberg → Postgres `raw_nba`

**Phase**: 4 — Expand Sports
**Functional unit**: NBA Iceberg tables → PostgreSQL `raw_nba` schema

## User Story
As a data engineer, I want the NBA Iceberg tables loaded into the `raw_nba` Postgres schema so that dbt can transform them.

## Scope
One hop: Iceberg → Postgres. Owns `src/domains/nba/loaders/iceberg_to_postgres.py` and the downstream load task.

## Acceptance Criteria

### Implementation
- [ ] loader reads each NBA Iceberg table and writes to `raw_nba`
- [ ] covers player_stats, game_logs, schedules
- [ ] idempotent (`if_exists="replace"`); `load_all_to_postgres()` entry point
- [ ] load task runs after ingestion completes

### Validation — unit / structural
- [ ] loader signatures, table coverage, replace semantics, `raw_nba` target

### Validation — k3s integration / data contract
- [ ] `raw_nba` contains the three tables after a load
- [ ] Postgres row counts match source Iceberg tables (within tolerance)
- [ ] metadata columns survive the round-trip; re-running does not duplicate rows

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
