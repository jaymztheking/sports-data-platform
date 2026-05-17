# MLB dbt Mart Models

**Phase**: 3 — Silver & Gold Layers
**Story Points**: 5

## User Story
As an analyst, I want gold-layer mart tables for MLB so that I can query season-level batting, pitching, and player data directly.

## Acceptance Criteria
- [x] `dim_mlb_players.sql` deduplicates players across batting and pitching, creates player dimension
- [x] `fct_mlb_batting_season.sql` selects season batting stats filtered to players with plate appearances
- [x] `fct_mlb_pitching_season.sql` selects season pitching stats filtered to players with innings pitched
- [x] `_mlb_marts.yml` defines column-level tests (not_null on IDs, seasons, key metrics)
- [x] All mart models materialized as tables
