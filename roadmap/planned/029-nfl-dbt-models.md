# NFL dbt Models

**Phase**: 4 — Expand Sports
**Story Points**: 5

## User Story
As an analyst, I want dbt staging and mart models for NFL so that I can query clean, aggregated NFL data.

## Acceptance Criteria
- [ ] `models/staging/nfl/_nfl_sources.yml` defines sources for `raw_nfl` tables
- [ ] `stg_nfl__play_by_play.sql` cleans play-level data
- [ ] `stg_nfl__weekly_stats.sql` standardizes weekly player stats
- [ ] `stg_nfl__rosters.sql` cleans roster data
- [ ] `stg_nfl__schedules.sql` cleans schedule data
- [ ] `models/marts/nfl/dim_nfl_players.sql` builds player dimension
- [ ] `models/marts/nfl/fct_nfl_team_season.sql` aggregates team season stats
- [ ] `models/marts/nfl/fct_nfl_player_weekly.sql` aggregates weekly player performance
- [ ] `_nfl_marts.yml` defines column tests
- [ ] `dags/nfl/nfl_transform_dag.py` orchestrates dbt run
