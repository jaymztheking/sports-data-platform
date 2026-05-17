# MLB dbt Staging Models

**Phase**: 3 — Silver & Gold Layers
**Story Points**: 5

## User Story
As a data engineer, I want dbt staging models that clean and standardize raw MLB data so that downstream marts have consistent, typed inputs.

## Acceptance Criteria
- [x] `_mlb_sources.yml` defines sources for all `raw_mlb` tables with freshness checks
- [x] `stg_mlb__statcast.sql` renames columns, casts types (game_id, speeds, angles, xBA, xwOBA)
- [x] `stg_mlb__batting.sql` maps FanGraphs column names to readable names (player_id_fg, batting_avg, ops, woba, war)
- [x] `stg_mlb__pitching.sql` standardizes pitching stats (era, whip, k_per_9, fip, war)
- [x] `stg_mlb__schedules.sql` cleans schedule data (game_date, team, opponent, result, pitchers)
- [x] All staging models materialized as views
