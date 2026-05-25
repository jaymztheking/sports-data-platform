# Cross-Sport: per-sport schedule marts → unified daily schedule

**Phase**: 4 — Expand Sports
**Functional unit**: MLB/NFL/NBA/NHL schedule marts → unified `fct_daily_schedule` table

## User Story
As an analyst, I want a unified daily schedule across all four sports so that I can see every game on any given day in one table.

## Scope
One transformation hop: unions the per-sport schedule marts into a single gold table. Depends on the schedule data from each sport's transform story (013, 017, 021, 024).

## Acceptance Criteria

### Implementation
- [ ] `models/marts/cross_sport/fct_daily_schedule.sql` unions schedule data from MLB, NFL, NBA, NHL
- [ ] standardized columns: `game_date`, `sport`, `home_team`, `away_team`, `result`
- [ ] materialized as a table in `marts`
- [ ] column tests defined (not_null on date/sport/teams)

### Validation — unit / structural
- [ ] compile succeeds; union covers all four sports; tests declared

### Validation — k3s integration / data contract
- [ ] `dbt build` produces `fct_daily_schedule` against real per-sport marts
- [ ] rows present for each sport that has loaded data
- [ ] no null game_date/sport; `sport` values limited to the four leagues
- [ ] `dbt test` passes

## Definition of Done
Unit/compile tests pass locally and the k3s integration class passes against real per-sport marts.
