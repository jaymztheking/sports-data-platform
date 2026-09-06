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

**2026-08-29 — S004/S005A merged, S007 promoted, roadmap sync PR (#9).** S004 (PR #4)
and S005A (PR #7) were already merged but `HANDOFF.md`/lane folders hadn't caught up —
`S004-staging-sources.md` moved `active/` → `completed/`. `S007` promoted from `backlog/`
to `planned/` with full acceptance criteria (it's the hard dependency S016 needs).

**2026-08-30 — S007 PR 1 in flight** on `s007-ingest-widening`: the 8 `nflreadpy`
loaders S016 needs (`pfr_advstats`, `team_stats`, `draft_picks`, `depth_charts`,
`ff_opportunity`, `snap_counts`) plus the 2026 `schedules` extension, all following the
existing `player_stats.py` ingest pattern. New `Settings.current_season` (2026) config
knob. 76 unit tests green (no network), ruff + mypy --strict clean, and every loader
smoke-tested against live nflreadpy data. ESPN/FFC ADP ingest + snapshotting + S008
samples are a separate PR 2 — see `roadmap/planned/S007-ingest-widening.md`.

## Board state

| Lane | Stories |
|------|---------|
| active | `S007` ingest widening (PR 1 built, not yet merged) |
| completed | `S001` foundation · `S002` dbt scaffold · `S003` ingest · `S003A` history window · `S004` staging · `S005A` `fct_player_season` draft board |
| planned | `S007` PR 2 (ADP ingest + snapshotting) → **`S016`–`S018` our own projections** (features → backtest → model) · `S006` CI + branch protection (post-draft) |
| deferred | `S005` `fct_player_week` → post-draft (in-season product) |
| backlog | `S008`–`S010` broaden products · `S011`–`S015` prod on k3s + BI + schedule |

Detailed acceptance criteria live in each `roadmap/<lane>/SNNN-*.md`.

## Next action

**Critical path to S018 (our own projections), not the 2026-09-05 draft anymore** — S007
→ S016 → S017 → S018 is real modelling work that won't land before drafts; the draft
board itself (`S005A`) already shipped and is usable as-is. Claude is writing these in
full per the rule-3 suspension; each still lands as its own reviewed PR with tests first.

1. ~~`S003`~~, ~~`S004`~~, ~~`S005A`~~, ~~roadmap sync (#9)~~ — merged.
2. **`S007` PR 1** (`s007-ingest-widening`) — built, tested, smoke-tested; **needs a PR
   opened and merged.**
3. **`S007` PR 2** — ESPN/FFC ADP ingest + snapshot mechanism + S008 samples. Not started.
4. **`S016`** — feature marts. Blocked on S007 PR 1 (minimum) landing.

**Run an ingest module:** `uv run python -m nfl.ingest.<module> [--season YYYY ...]` from
the repo root; writes to `NFL_DATA_DIR` (default `data/raw`).

**Run the dbt build:** `NFL_DATA_DIR=data/raw uv run dbt build --project-dir dbt_project
--profiles-dir dbt_project` from the repo root (paths in `external_location` are relative
to cwd). CI swaps in `NFL_DATA_DIR=data/samples NFL_DUCKDB_PATH=:memory:`.

Note: CI still does not run dbt (and does not lint `scripts/` or run sqlfluff) — that
wiring is **S006**, deferred until after the projection stories. Until then the local
`dbt build` on both `data/samples` and `data/raw` is the gate.

Known local-only issue: `pytest` on this Windows checkout fails 3 pre-existing
`*_adds_metadata` tests with `ZoneInfoNotFoundError: No time zone found with key UTC` — a
polars/zoneinfo resource-lookup quirk in this venv, reproduces on `main` too, unrelated to
any story's changes. Run `pytest -k "not adds_metadata and not stamps_one_utc"` locally to
skip it; CI (Linux) is not expected to hit it.

## Notes / decisions

- **Draft board artifact** — published page over `fct_player_season`. ECR refreshed
  2026-09-06 (board scraped 2026-09-04) for the second league draft. Sticky-header bug
  fixed the same day (`S005B`). Its **generator is not in the repo** — regenerated from a
  query each time. Put it under version control before the next refresh.

- Cost rule: always-free or self-hosted only (no trials/tiers, no MotherDuck).
- Engines: two environments — `dev` = DuckDB, `prod` = Postgres on simplified k3s (two dbt adapters). CI is the dev→prod gate (runs `dev` on `:memory:`), not a third env.
- Collaboration: **rule 3 suspended 2026-08-28 → 2026-09-06** (draft). Claude writes core SQL/Python in full until then; restore after. PR-per-story + TDD unaffected (see `CLAUDE.md`).
- Open (decide at S014): BI tool — Evidence.dev vs Metabase.
