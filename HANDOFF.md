# HANDOFF

> Read this first each session, then `CLAUDE.md` for durable rules.

## Where we are

**2026-07-13 — NFL pivot.** The old MLB/multi-sport platform (k3s + Spark + Iceberg + MinIO + Airflow + MLflow) was torn down. We are rebuilding as a focused **NFL fantasy-football platform centered on dbt**, shipping working data products on light local tooling first and adding self-hosted infra last. See the approved plan and `CLAUDE.md`.

**2026-07-15 — S001 merged.** PR #1 (`s001-foundation` → `main`) merged at `12be449`; `main` is now the NFL foundation. `S001` → `completed/`.

**2026-07-30 — S002 merged.** PR #2 (`s002-dbt-scaffold` → `main`) merged at `3c9d560`. dbt project lives in `dbt_project/` with **two targets** — `dev` (DuckDB) / `prod` (Postgres via `env_var`); **CI is the dev→prod gate**, running the `dev` target ephemerally (`NFL_DUCKDB_PATH=:memory:`) — there is no `ci` target. `S002` → `completed/`.

**2026-07-30 — S003 in flight.** Ingest scaffold on branch `s003-ingest-weekly-schedules`.

**2026-08-28 — draft deadline; hand-coding suspended; roadmap re-aimed.** Fantasy drafts
are **2026-09-05 (8 days out)**. Two decisions:

1. **`CLAUDE.md` rule 3 (division of labor) is SUSPENDED until 2026-09-06.** Claude may
   write core SQL/Python in full through the draft. Rules 1/2/4 (PR-per-story, TDD-first,
   small PRs) **still bind** — they carry the anti-pile load. Restore text is in `CLAUDE.md`.
2. **`S005 fct_player_week` is deferred to post-draft.** It is the wrong grain for draft
   prep — on 2026-09-05 the 2026 season has not kicked off, so there are no 2026 weekly
   rows. New story **`S005A fct_player_season`** (draft board) takes its slot: 2025
   season-grain per-game rates + positional ranks + `load_ff_rankings` ECR join →
   value-over-ECR (the feed has no `adp` column — see S005A). `S005` returns as the in-season product after kickoff.

**S003 actual state** (uncommitted on the branch, ahead of what this file used to say):
`src/nfl/ingest/player_stats.py` core is **written** (real `nfl.load_player_stats`,
metadata cols, argparse CLI); `src/nfl/ingest/_common.py` added (`add_metadata` /
`write_parquet`). Still open: `schedules.py` is a stub, new `ff_rankings.py` not started,
`tests/ingest/test_player_stats.py` still `pytest.mark.skip`, `data/samples/` empty.

## Board state

| Lane | Stories |
|------|---------|
| active | `S003` ingest player stats + schedules **+ ff_rankings** — player_stats done, rest open |
| completed | `S001` foundation · `S002` dbt scaffold |
| planned | `S004` staging + sources · **`S005A` `fct_player_season` (draft board — the 09-05 target)** · `S006` CI + branch protection |
| deferred | `S005` `fct_player_week` → post-draft (in-season product) |
| backlog | `S007`–`S010` broaden products · `S011`–`S015` prod on k3s + BI + schedule |

Detailed acceptance criteria live in each `roadmap/<lane>/SNNN-*.md`.

## Next action

**Critical path to 2026-09-05 (drafts).** Claude is writing these in full per the rule-3
suspension; each still lands as its own reviewed PR with tests first.

1. **Finish `S003`** — `schedules.py`, new `ff_rankings.py`, un-skip + extend the ingest
   tests, commit the `data/samples/` slice. PR → `main`.
2. **`S004`** — `_nfl__sources.yml` + `stg_nfl__{player_stats,schedules,ff_rankings}`.
3. **`S005A`** — `fct_player_season` draft board + `scoring_rules.csv` seed.

Note: CI still does not run dbt — that wiring is **S006**, and it stays *after* the draft.
Until then `dbt build --target dev` is run locally as the gate.

## Notes / decisions

- Cost rule: always-free or self-hosted only (no trials/tiers, no MotherDuck).
- Engines: two environments — `dev` = DuckDB, `prod` = Postgres on simplified k3s (two dbt adapters). CI is the dev→prod gate (runs `dev` on `:memory:`), not a third env.
- Collaboration: **rule 3 suspended 2026-08-28 → 2026-09-06** (draft). Claude writes core SQL/Python in full until then; restore after. PR-per-story + TDD unaffected (see `CLAUDE.md`).
- Open (decide at S014): BI tool — Evidence.dev vs Metabase.
