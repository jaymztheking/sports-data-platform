# HANDOFF

> Read this first each session, then `CLAUDE.md` for durable rules.

## Where we are

**2026-07-13 — NFL pivot.** The old MLB/multi-sport platform (k3s + Spark + Iceberg + MinIO + Airflow + MLflow) was torn down. We are rebuilding as a focused **NFL fantasy-football platform centered on dbt**, shipping working data products on light local tooling first and adding self-hosted infra last. See the approved plan and `CLAUDE.md`.

## Board state

| Lane | Stories |
|------|---------|
| active | `S001` foundation (repo reset + tooling + docs + roadmap) — **in progress** |
| planned | `S002` dbt scaffold + 3 targets · `S003` ingest weekly+schedules · `S004` staging + sources · `S005` `fct_player_week` (first product) · `S006` CI + branch protection |
| backlog | `S007`–`S010` broaden products · `S011`–`S015` prod on k3s + BI + schedule |

Detailed acceptance criteria live in each `roadmap/<lane>/SNNN-*.md`.

## Next action

Finish `S001`: land `pyproject.toml`, docs, roadmap, agent updates, and a green lint/type/test gate via PR. Then start `S002` (dbt project scaffold with `dev`/`ci`/`prod` targets and one proving staging model on DuckDB).

## Notes / decisions

- Cost rule: always-free or self-hosted only (no trials/tiers, no MotherDuck).
- Engines: dev/ci = DuckDB, prod = Postgres on simplified k3s. Two dbt adapters.
- Collaboration: Claude scaffolds; James hand-writes core SQL/Python (see `CLAUDE.md`).
- Open (decide at S014): BI tool — Evidence.dev vs Metabase.
