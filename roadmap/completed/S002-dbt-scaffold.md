# S002 — dbt scaffold + two targets + proving model

**Phase**: 0 — Foundation
**Functional unit**: a runnable dbt project with `dev`/`prod` targets, gated by CI

## User Story
As the developer, I want a dbt project wired for two environments (dev/prod) with
CI as the promotion gate between them, so that env separation (the portfolio
headline) is real from the first model onward.

## Scope
dbt project scaffold only. One trivial proving staging model to confirm `dbt build`
works on DuckDB `dev`. No NFL data yet (uses a hardcoded/seeded row or a tiny sample).

## Environments vs. CI
Two **environments**: `dev` (DuckDB, local) and `prod` (Postgres, k3s). **CI is not a
third environment** — it is the mechanism that gates dev → prod by running the `dev`
target ephemerally (`NFL_DUCKDB_PATH=:memory:`) against the committed sample on every
PR. The prod-deploy story later runs the same build/contracts on Postgres to catch
cross-adapter drift. (Wiring dbt into the CI workflow itself is **S006**.)

## Acceptance Criteria

### Implementation
- [ ] `dbt_project/dbt_project.yml` — layer materializations (staging=view, marts=table), `nfl` tags
- [ ] `dbt_project/profiles.yml` — `dev` (duckdb, `NFL_DUCKDB_PATH` → file locally / `:memory:` in CI), `prod` (postgres via `env_var`)
- [ ] `dbt_project/packages.yml` — `dbt_utils`, `dbt_expectations`
- [ ] `dbt_project/macros/generate_schema_name.sql` — schema by `target.name`
- [ ] one proving model (e.g. `stg_nfl__hello`) that compiles + materializes

### Validation — unit / structural
- [ ] `dbt deps` + `dbt parse` succeed
- [ ] `dbt build --target dev` builds the local `nfl.duckdb`
- [ ] `NFL_DUCKDB_PATH=:memory: dbt build --target dev` runs green ephemerally (the CI path)
- [ ] `prod` target resolves from `env_var` and honors custom schema names (verified at prod-deploy)

## Definition of Done
`dbt build` green on the `dev` target both persistently and ephemerally (`:memory:`);
prod target parses; env separation via `generate_schema_name` verified.
