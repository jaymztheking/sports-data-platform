# NBA Silver+Gold: `raw_nba` → dbt staging + marts

**Phase**: 4 — Expand Sports
**Functional unit**: PostgreSQL `raw_nba` → dbt staging views + mart tables

## User Story
As an analyst, I want raw NBA data transformed through dbt into clean staging and gold marts so that I can query player season data.

## Scope
One transformation hop via dbt. Owns sources, staging models, mart models, column tests, and the NBA transform DAG.

## Acceptance Criteria

### Implementation
- [ ] `_nba_sources.yml` for `raw_nba` tables
- [ ] staging models: player_stats, game_logs, schedules (cleaned, typed, views)
- [ ] marts: `dim_nba_players`, `fct_nba_player_season` (tables)
- [ ] `_nba_marts.yml` column tests
- [ ] transform DAG runs staging → marts → tests

### Validation — unit / structural
- [ ] compile succeeds; materializations and tags correct; tests declared

### Validation — k3s integration / data contract
- [ ] `dbt build --select tag:nba` succeeds against real `raw_nba` data
- [ ] staging views and mart tables created in correct schemas
- [ ] `dbt test --select tag:nba` passes
- [ ] gold tables queryable with expected data

## Definition of Done
Unit/compile tests pass locally and the k3s integration class passes against real loaded data.
