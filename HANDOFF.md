# HANDOFF

> Read this first each session, then `CLAUDE.md` for durable rules.

## Where we are

**2026-07-13 — NFL pivot.** The old MLB/multi-sport platform (k3s + Spark + Iceberg + MinIO + Airflow + MLflow) was torn down. We are rebuilding as a focused **NFL fantasy-football platform centered on dbt**, shipping working data products on light local tooling first and adding self-hosted infra last. See the approved plan and `CLAUDE.md`.

**2026-07-15 — S001 merged.** PR #1 (`s001-foundation` → `main`) merged at `12be449`; `main` is now the NFL foundation. `S001` → `completed/`.

**2026-07-30 — S002 merged.** PR #2 (`s002-dbt-scaffold` → `main`) merged at `3c9d560`. dbt project lives in `dbt_project/` with **two targets** — `dev` (DuckDB) / `prod` (Postgres via `env_var`); **CI is the dev→prod gate**, running the `dev` target ephemerally (`NFL_DUCKDB_PATH=:memory:`) — there is no `ci` target. `S002` → `completed/`.

**2026-07-30 — S003 in flight.** Ingest scaffold on branch `s003-ingest-weekly-schedules`: `src/nfl/config.py` (pydantic-settings **reference impl**), `src/nfl/ingest/{player_stats,schedules}.py` **stubs** (`fetch_player_stats`/`fetch_schedules` raise `NotImplementedError`), and a **skipped reference test** `tests/ingest/test_player_stats.py` showing the no-network mock pattern. **James's pickup:** hand-write the `nflreadpy` fetch + Polars transform (add `ingested_at`/`source` cols), wire the `python -m nfl.ingest.*` CLI to write Parquet, commit the `data/samples/` slice, then un-skip + flesh out the tests.

## Board state

| Lane | Stories |
|------|---------|
| active | `S003` ingest player stats + schedules — scaffold laid, **awaiting James's core Polars** |
| completed | `S001` foundation · `S002` dbt scaffold |
| planned | `S004` staging + sources · `S005` `fct_player_week` (first product) · `S006` CI + branch protection |
| backlog | `S007`–`S010` broaden products · `S011`–`S015` prod on k3s + BI + schedule |

Detailed acceptance criteria live in each `roadmap/<lane>/SNNN-*.md`.

## Next action

1. **James:** hand-write the S003 core in `src/nfl/ingest/{player_stats,schedules}.py` (nflreadpy fetch + transform + metadata + CLI), commit the `data/samples/` slice, un-skip `tests/ingest/test_player_stats.py` and add the schedules test. Then PR `s003-ingest-weekly-schedules` → `main`.
2. Then `S004` (staging models + `sources.yml` on the ingested Parquet).

Note: CI still does not run dbt — that wiring is **S006**.

## Notes / decisions

- Cost rule: always-free or self-hosted only (no trials/tiers, no MotherDuck).
- Engines: two environments — `dev` = DuckDB, `prod` = Postgres on simplified k3s (two dbt adapters). CI is the dev→prod gate (runs `dev` on `:memory:`), not a third env.
- Collaboration: Claude scaffolds; James hand-writes core SQL/Python (see `CLAUDE.md`).
- Open (decide at S014): BI tool — Evidence.dev vs Metabase.
