# NHL dbt Models

**Phase**: 4 — Expand Sports
**Story Points**: 5

## User Story
As an analyst, I want dbt staging and mart models for NHL so that I can query clean, aggregated NHL data.

## Acceptance Criteria
- [ ] `models/staging/nhl/_nhl_sources.yml` defines sources for `raw_nhl` tables
- [ ] `stg_nhl__game_stats.sql` cleans game-level stats
- [ ] `stg_nhl__player_stats.sql` standardizes player season stats
- [ ] `stg_nhl__schedules.sql` cleans schedule data
- [ ] `models/marts/nhl/dim_nhl_players.sql` builds player dimension
- [ ] `models/marts/nhl/fct_nhl_player_season.sql` aggregates season stats
- [ ] `_nhl_marts.yml` defines column tests
- [ ] `dags/nhl/nhl_transform_dag.py` orchestrates dbt run
