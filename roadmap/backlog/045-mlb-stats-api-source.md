# MLB Statcast & Stats API Source for Batting and Pitching

**Phase**: 2 — Pipeline
**Story Points**: 3

## User Story
As a data engineer, I want batting and pitching stats sourced from official MLB APIs instead of scraped HTML so that the pipeline is free from Fangraphs scraping blocks and gets richer Statcast metrics.

## Background
`pybaseball.batting_stats()` / `pitching_stats()` scraped `fangraphs.com/leaders-legacy.aspx`. As of April 2026 Fangraphs requires CAPTCHA verification, permanently breaking those functions (see pybaseball #507). The interim fix (story 011) switched to Baseball Reference via `batting_stats_bref()` / `pitching_stats_bref()`.

Two official MLB sources exist and can be combined:

### 1 — Baseball Savant Statcast Leaderboard API (preferred for Statcast metrics)
Baseball Savant exposes undocumented JSON/CSV endpoints used internally by their website. These return player-season Statcast aggregates (xBA, xSLG, xwOBA, barrel%, hard-hit%, sprint speed, etc.) — richer than anything Fangraphs had. Key endpoints:

- **Expected stats** (batter): `https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=batter&year={season}&min=q&csv=true`
- **Expected stats** (pitcher): `https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=pitcher&year={season}&min=q&csv=true`
- **Custom leaderboard**: `https://baseballsavant.mlb.com/leaderboard/custom?year={season}&type=batter&csv=true&selections=...`
- **Pitch-level raw** (existing `statcast()` call): `https://baseballsavant.mlb.com/statcast_search/csv?...`

Baseball Savant is operated by MLB and doesn't have CAPTCHA / anti-scraping measures against reasonable programmatic use. pybaseball's `statcast()` already calls it — these leaderboard endpoints follow the same pattern.

### 2 — MLB Stats API (for traditional counting stats)
`https://statsapi.mlb.com/api/v1/stats?stats=season&season={year}&group=hitting&playerPool=All&limit=2000`
Returns official traditional counting stats (AB, H, HR, RBI, AVG, OBP, SLG). Free, unauthenticated, JSON. Also see `group=pitching` for ERA, W, L, K, etc.

## Acceptance Criteria

### Implementation
- [ ] Replace `batting_stats_bref()` in `batting.py` with Baseball Savant expected-stats endpoint (batter leaderboard)
- [ ] Replace `pitching_stats_bref()` in `pitching.py` with Baseball Savant expected-stats endpoint (pitcher leaderboard)
- [ ] Optionally merge with MLB Stats API traditional counts (join on player ID)
- [ ] Column names documented; metadata columns (`ingested_at`, `source`, `season`) preserved
- [ ] `source` value updated to `baseball_savant.leaderboard.batter` / `baseball_savant.leaderboard.pitcher`

### Validation — unit/structural
- [ ] Unit tests confirm API response parses into a non-empty DataFrame with expected columns
- [ ] Schema contract tests pass locally (no Fangraphs calls)

### Validation — k3s integration
- [ ] k3s integration test ingests batting and pitching for one season without any Fangraphs or bref dependency
- [ ] Row counts positive, metadata columns present, season partition written to Iceberg
