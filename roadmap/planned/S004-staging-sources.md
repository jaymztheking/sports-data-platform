# S004 — Staging + sources (cross-adapter)

**Phase**: 1 — Thin vertical slice
**Functional unit**: raw Parquet/tables → `stg_nfl__weekly`, `stg_nfl__schedules`

## User Story
As an analyst, I want cleaned, typed staging views so that marts build on stable inputs.

## Scope
Define `raw_nfl` sources once, resolving in both engines (DuckDB `external_location`
meta over Parquet; real tables in Postgres). Staging SQL is engine-agnostic. James
hand-writes the staging SQL; Claude scaffolds `_nfl__sources.yml` + one reference model.

## Acceptance Criteria

### Implementation
- [ ] `models/staging/nfl/_nfl__sources.yml` — `raw_nfl` sources w/ freshness + `external_location` meta for DuckDB
- [ ] `stg_nfl__weekly.sql`, `stg_nfl__schedules.sql` — typed/renamed/cleaned views
- [ ] `_nfl__staging.yml` — column tests (not_null/unique on keys)

### Validation — unit / structural
- [ ] `dbt build --target dev` on sample data (`NFL_DUCKDB_PATH=:memory:`, the CI path): staging views build, tests pass
- [ ] source freshness config parses

## Definition of Done
Staging views build and pass tests on the `ci` sample; sources resolve on DuckDB.
