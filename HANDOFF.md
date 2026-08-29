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

**2026-08-28 — S003 merged.** PR #3 merged at `580785f`. All three ingest modules run
(`player_stats`, `schedules`, `ff_rankings`), 20 no-network tests, `data/samples/` slice
committed, `scripts/make_samples.py` regenerates it. `S003` → `completed/`.

**2026-08-28 — S003A: history widened to 2022–2025.** Measured what the draft board
would stand on and found **one season**. Ingest now pulls a configurable window
(`NFL_HISTORY_START_SEASON`, default 2022): **75,879 player-weeks / 1,139 games**, and the
average top-50 board player carries **49.4 games** of history instead of ~14. Widening
further is one env var — deferred to backlog on time, not on merit; James wants
materially more history post-draft.

**2026-08-28 — S004 in flight** on `s004-staging-sources`: `raw_nfl` sources +
`stg_nfl__{player_stats,schedules,ff_rankings}` + `normalize_player_name` macro +
`.sqlfluff`. Green on both the sample and the full season (22/22), freshness passes.

## Board state

| Lane | Stories |
|------|---------|
| active | `S004` staging + sources (PR #4) · `S003A` multi-season history (PR #5, stacked on #4) |
| completed | `S001` foundation · `S002` dbt scaffold · `S003` ingest · `S003A` history window |
| planned | **`S005A` `fct_player_season` (draft board — the 09-05 target)** · `S006` CI + branch protection |
| deferred | `S005` `fct_player_week` → post-draft (in-season product) |
| backlog | `S007`–`S010` broaden products · `S011`–`S015` prod on k3s + BI + schedule |

Detailed acceptance criteria live in each `roadmap/<lane>/SNNN-*.md`.

## Next action

**Critical path to 2026-09-05 (drafts).** Claude is writing these in full per the rule-3
suspension; each still lands as its own reviewed PR with tests first.

1. ~~`S003`~~ merged (PR #3).
2. **`S004`** — built and green; PR open, needs review/merge.
3. **`S005A`** — `fct_player_season` draft board + `scoring_rules.csv` seed. **Next build.**

**Carry into S005A — the one place the board can still be silently wrong:**
`player_join_key + position` is not unique on the draft board (two distinct WRs named
*Isaiah Williams*). The join must dedupe deliberately, preferring the rostered entry over
the free agent, with a `unique` test on the mart grain proving it. The name key itself is
solved — `normalize_player_name` strips generational suffixes and now matches 100% of the
top-100 2025 producers (before stripping, Mahomes/Cook/Etienne/Pitts fell off the board).

**Run the build:** `NFL_DATA_DIR=data/raw uv run dbt build --project-dir dbt_project
--profiles-dir dbt_project` from the repo root (paths in `external_location` are relative
to cwd). CI swaps in `NFL_DATA_DIR=data/samples NFL_DUCKDB_PATH=:memory:`.

Note: CI still does not run dbt (and does not lint `scripts/` or run sqlfluff) — that
wiring is **S006**, which stays *after* the draft. Until then the local `dbt build` on both
`data/samples` and `data/raw` is the gate.

## Notes / decisions

- Cost rule: always-free or self-hosted only (no trials/tiers, no MotherDuck).
- Engines: two environments — `dev` = DuckDB, `prod` = Postgres on simplified k3s (two dbt adapters). CI is the dev→prod gate (runs `dev` on `:memory:`), not a third env.
- Collaboration: **rule 3 suspended 2026-08-28 → 2026-09-06** (draft). Claude writes core SQL/Python in full until then; restore after. PR-per-story + TDD unaffected (see `CLAUDE.md`).
- Open (decide at S014): BI tool — Evidence.dev vs Metabase.
