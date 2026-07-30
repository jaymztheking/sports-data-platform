# S002 — dbt scaffold + three targets + proving model

**Phase**: 0 — Foundation
**Functional unit**: a runnable dbt project with dev/ci/prod targets on DuckDB

## User Story
As the developer, I want a dbt project wired for three environments so that env
separation (the portfolio headline) is real from the first model onward.

## Scope
dbt project scaffold only. One trivial proving staging model to confirm `dbt build`
works on DuckDB `dev`. No NFL data yet (uses a hardcoded/seeded row or a tiny sample).

## Acceptance Criteria

### Implementation
- [ ] `dbt_project/dbt_project.yml` — layer materializations (staging=view, marts=table), `nfl` tags
- [ ] `dbt_project/profiles.yml` — `dev` (duckdb file), `ci` (duckdb `:memory:`), `prod` (postgres via `env_var`)
- [ ] `dbt_project/packages.yml` — `dbt_utils`, `dbt_expectations`
- [ ] `dbt_project/macros/generate_schema_name.sql` — schema by `target.name`
- [ ] one proving model (e.g. `stg_nfl__hello`) that compiles + materializes

### Validation — unit / structural
- [ ] `dbt deps` + `dbt parse` succeed
- [ ] `dbt build --target dev` builds `nfl.duckdb`; `dbt build --target ci` runs on `:memory:`
- [ ] schema naming differs correctly between `dev` and `ci`

## Definition of Done
`dbt build` green on `dev` and `ci` targets; schema-per-target behavior verified.
