# MLB Silver+Gold: `raw_mlb` → dbt staging + marts

**Phase**: 3 — Silver & Gold Layers
**Functional unit**: PostgreSQL `raw_mlb` → dbt staging views + mart tables

## User Story
As an analyst, I want raw MLB data transformed through dbt into clean staging views and gold mart tables so that I can query season-level batting, pitching, and player data directly.

## Scope
One transformation hop, one tool (dbt), one orchestration (transform DAG). Owns the dbt project scaffold, sources, staging models, intermediate models where useful, mart models, the team reference seed, and the Airflow transform DAG. Staging and marts are not split into separate stories — they are intermediate layers within the same dbt build.

## Acceptance Criteria

### Implementation
- [ ] dbt project configured for Postgres: staging as views, marts as tables, schema routing per layer, dbt-utils, per-sport/per-layer tags
- [ ] `_mlb_sources.yml` defines `raw_mlb` sources with freshness checks
- [ ] Staging models clean/standardize statcast, batting, pitching, schedules (typed, readable column names)
- [ ] Mart models: `dim_mlb_players`, `fct_mlb_batting_season`, `fct_mlb_pitching_season`
- [ ] `mlb_teams.csv` seed (30 teams: abbrev, name, league, division)
- [ ] Transform DAG runs staging → marts → tests, triggered downstream of the loader

### Validation — unit / structural
- [ ] `dbt parse`/compile succeeds; models carry correct materializations and tags
- [ ] mart `_mlb_marts.yml` declares not_null/unique tests on IDs, seasons, key metrics

### Validation — k3s integration / data contract (against real `raw_mlb` data)
- [ ] `dbt build --select tag:mlb` succeeds end to end
- [ ] staging views exist in `staging` schema; mart tables exist in `marts` schema
- [ ] `dbt test --select tag:mlb` passes all not_null/unique tests
- [ ] `dbt seed` loads `mlb_teams.csv` (30 rows)
- [ ] gold tables queryable with expected data (batting leaders, pitching stats)

## Definition of Done
Unit/compile tests pass locally and the k3s integration class passes against real loaded data.
