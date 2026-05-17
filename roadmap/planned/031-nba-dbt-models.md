# NBA dbt Models

**Phase**: 4 — Expand Sports
**Story Points**: 5

## User Story
As an analyst, I want dbt staging and mart models for NBA so that I can query clean, aggregated NBA data.

## Acceptance Criteria
- [ ] `models/staging/nba/_nba_sources.yml` defines sources for `raw_nba` tables
- [ ] `stg_nba__player_stats.sql` standardizes player season stats
- [ ] `stg_nba__game_logs.sql` cleans game-level logs
- [ ] `stg_nba__schedules.sql` cleans schedule data
- [ ] `models/marts/nba/dim_nba_players.sql` builds player dimension
- [ ] `models/marts/nba/fct_nba_player_season.sql` aggregates season stats
- [ ] `_nba_marts.yml` defines column tests
- [ ] `dags/nba/nba_transform_dag.py` orchestrates dbt run
