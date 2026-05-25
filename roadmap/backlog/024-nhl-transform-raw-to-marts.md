# NHL Silver+Gold: `raw_nhl` → dbt staging + marts

**Phase**: 4 — Expand Sports
**Functional unit**: PostgreSQL `raw_nhl` → dbt staging views + mart tables

## User Story
As an analyst, I want raw NHL data transformed through dbt into clean staging and gold marts so that I can query player season data.

## Scope
One transformation hop via dbt. Owns sources, staging models, mart models, column tests, and the NHL transform DAG.

## Acceptance Criteria

### Implementation
- [ ] `_nhl_sources.yml` for `raw_nhl` tables
- [ ] staging models: game_stats, player_stats, schedules (cleaned, typed, views)
- [ ] marts: `dim_nhl_players`, `fct_nhl_player_season` (tables)
- [ ] `_nhl_marts.yml` column tests
- [ ] transform DAG runs staging → marts → tests

### Validation — unit / structural
- [ ] compile succeeds; materializations and tags correct; tests declared

### Validation — k3s integration / data contract
- [ ] `dbt build --select tag:nhl` succeeds against real `raw_nhl` data
- [ ] staging views and mart tables created in correct schemas
- [ ] `dbt test --select tag:nhl` passes
- [ ] gold tables queryable with expected data

## Definition of Done
Unit/compile tests pass locally and the k3s integration class passes against real loaded data.
