# HANDOFF

> Read this first each session, then `CLAUDE.md` for durable rules.

## Where we are

**2026-07-13 — NFL pivot.** The old MLB/multi-sport platform (k3s + Spark + Iceberg + MinIO + Airflow + MLflow) was torn down. We are rebuilding as a focused **NFL fantasy-football platform centered on dbt**, shipping working data products on light local tooling first and adding self-hosted infra last. See the approved plan and `CLAUDE.md`.

**2026-07-15 — S001 merged.** PR #1 (`s001-foundation` → `main`) merged at `12be449`; `main` is now the NFL foundation. `S001` → `completed/`.

**2026-07-29 — S002 in flight.** dbt project scaffolded on branch `s002-dbt-scaffold`: `dbt_project.yml` (layer materializations + `nfl` tag), `profiles.yml` (`dev` file DuckDB / `ci` `:memory:` / `prod` Postgres via `env_var`), `packages.yml` (`dbt_utils`, `dbt_expectations`), `generate_schema_name` keyed on `target.name`, and a proving model `stg_nfl__hello`. `dbt deps`/`parse`/`build` green on **dev** (schema `dev`) and **ci** (schema `ci`) — schema-per-target verified. PR pending.

## Board state

| Lane | Stories |
|------|---------|
| validating | `S002` dbt scaffold — local green on dev/ci, **PR pending** |
| completed | `S001` foundation |
| planned | `S003` ingest weekly+schedules · `S004` staging + sources · `S005` `fct_player_week` (first product) · `S006` CI + branch protection |
| backlog | `S007`–`S010` broaden products · `S011`–`S015` prod on k3s + BI + schedule |

Detailed acceptance criteria live in each `roadmap/<lane>/SNNN-*.md`.

## Next action

1. Open the **S002** PR (`s002-dbt-scaffold` → `main`); merge once CI green. Then `S002` → `completed/`.
2. Start **`S003`** (ingest weekly stats + schedules with `nflreadpy` → Parquet in `data/raw/`, sample committed for CI) on a fresh `s003-*` branch. Claude scaffolds the ingest skeleton; James hand-writes the core Polars fetch/transform.

Note: S002 CI does not yet run dbt — wiring `dbt build --target ci` into the GitHub workflow is **S006**.

## Notes / decisions

- Cost rule: always-free or self-hosted only (no trials/tiers, no MotherDuck).
- Engines: dev/ci = DuckDB, prod = Postgres on simplified k3s. Two dbt adapters.
- Collaboration: Claude scaffolds; James hand-writes core SQL/Python (see `CLAUDE.md`).
- Open (decide at S014): BI tool — Evidence.dev vs Metabase.
