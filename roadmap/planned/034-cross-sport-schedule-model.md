# Cross-Sport Daily Schedule Model

**Phase**: 4 — Expand Sports
**Story Points**: 3

## User Story
As an analyst, I want a unified daily schedule across all 4 sports so that I can see all games happening on any given day.

## Acceptance Criteria
- [ ] `models/marts/cross_sport/fct_daily_schedule.sql` unions schedule data from MLB, NFL, NBA, NHL
- [ ] Columns standardized: game_date, sport, home_team, away_team, result
- [ ] Model materialized as a table in `marts` schema
- [ ] Column tests defined
