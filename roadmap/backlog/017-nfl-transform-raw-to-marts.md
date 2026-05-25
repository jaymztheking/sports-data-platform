# NFL Silver+Gold: `raw_nfl` → dbt staging + marts

**Phase**: 4 — Expand Sports
**Functional unit**: PostgreSQL `raw_nfl` → dbt staging views + mart tables

## User Story
As an analyst, I want raw NFL data transformed through dbt into clean staging and gold marts so that I can query player and team season data.

## Scope
One transformation hop via dbt. Owns sources, staging models, mart models, column tests, and the NFL transform DAG.

## Acceptance Criteria

### Implementation
- [ ] `_nfl_sources.yml` for `raw_nfl` tables
- [ ] staging models: play_by_play, weekly_stats, rosters, schedules (cleaned, typed, views)
- [ ] marts: `dim_nfl_players`, `fct_nfl_team_season`, `fct_nfl_player_weekly` (tables)
- [ ] `_nfl_marts.yml` column tests
- [ ] transform DAG runs staging → marts → tests

### Validation — unit / structural
- [ ] compile succeeds; materializations and tags correct; tests declared

### Validation — k3s integration / data contract
- [ ] `dbt build --select tag:nfl` succeeds against real `raw_nfl` data
- [ ] staging views and mart tables created in correct schemas
- [ ] `dbt test --select tag:nfl` passes
- [ ] gold tables queryable with expected data

## Definition of Done
Unit/compile tests pass locally and the k3s integration class passes against real loaded data.
