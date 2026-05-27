# MLB Stats API Source for Batting and Pitching

**Phase**: 2 — Pipeline
**Story Points**: 3

## User Story
As a data engineer, I want batting and pitching stats sourced from the official MLB Stats API instead of Fangraphs so that the pipeline is free from scraping rate limits and third-party availability.

## Background
`pybaseball.batting_stats()` and `pybaseball.pitching_stats()` scrape `fangraphs.com/leaders-legacy.aspx`, which rate-limits aggressively. The MLB Stats API (`statsapi.mlb.com`) is the official, free, unauthenticated REST API and covers standard counting/rate stats. Advanced Fangraphs-only metrics (wRC+, FIP) would be dropped unless separately sourced.

## Acceptance Criteria

### Implementation
- [ ] Replace `pybaseball.batting_stats()` in `batting.py` with MLB Stats API call (`statsapi.mlb.com/api/v1/stats?stats=season&group=hitting`)
- [ ] Replace `pybaseball.pitching_stats()` in `pitching.py` with MLB Stats API call (`statsapi.mlb.com/api/v1/stats?stats=season&group=pitching`)
- [ ] Column names normalized to match or supersede prior Fangraphs schema
- [ ] Metadata columns (`ingested_at`, `source`, `season`) preserved
- [ ] `source` value updated to `mlb_stats_api.batting` / `mlb_stats_api.pitching`

### Validation — unit/structural
- [ ] Unit tests confirm API response is parsed into a non-empty DataFrame
- [ ] Schema contract tests pass locally

### Validation — k3s integration
- [ ] k3s integration test ingests batting and pitching for one season without Fangraphs dependency
- [ ] Row counts positive, metadata columns present, season partition written to Iceberg
