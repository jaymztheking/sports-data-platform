# S007 — Ingest widening: projection inputs + ADP/ECR snapshotting

**Phase**: 2 — Our own projections
**Functional unit**: `nflreadpy` + two new public JSON APIs → Parquet, widening ingest to
cover everything S016's feature marts (and S008's usage intermediates) need

> Promoted out of `roadmap/backlog/S007-S015-later-phases.md` 2026-08-29. **Hard
> dependency: S007 → S016, S007 → S008.** Neither can build without this landing first.

> **2026-08-30 — split into two PRs.** The 8 `nflreadpy` loaders + the 2026 schedule
> extension are one PR (`s007-ingest-widening`) — they all follow the exact
> `player_stats.py`/`schedules.py` pattern already in the repo. ESPN/FFC ADP ingest,
> the snapshot mechanism, and the S008-only samples (`pbp`/`rosters_weekly`/`injuries`)
> are genuinely new engineering (new HTTP APIs, new append-don't-overwrite behavior)
> and follow as a second PR. Checkboxes below are marked per PR.

## User Story
As the projection pipeline, I need environment/role/ADP inputs sitting on disk as Parquet
so that S016's feature marts have real data to build on, and so ECR/ADP have a history to
backtest against starting now instead of a year from now.

## Scope
Eight `nflreadpy` loaders no prior story pulls, plus two brand-new non-`nflreadpy` JSON
APIs (ESPN ADP, FFC ADP) that need their own ingest modules. Also stands up dated
snapshotting for the two sources that are live-only snapshots — first snapshot happens on
this story's build, not retroactively.

No feature computation, no cross-source joins beyond keying each source to
`player_id`/`ff_player_id` — that's S016 (features) and S008 (usage/opportunity).

### Supersedes one earlier call
The original backlog note listed `load_ff_opportunity` and `load_ff_rankings` as
"deliberately out" — ingesting someone else's finished fantasy analytics would make our
marts a wrapper around their model. `ff_rankings` is already ingested (S003, for ECR).
`ff_opportunity` is now **in**: S016 needs its `*_exp` (luck-stripped) columns as one input
among several to a feature, which is a different thing from consuming it as a finished
ranking. The "no wrapper" principle still holds downstream — `ff_opportunity` feeds a
feature, not the projection output itself.

### `nflreadpy` loaders (8)
| Loader | Feeds | Note |
|---|---|---|
| `load_pfr_advstats(stat_type='rush')` | S016 `int_team_line_quality` | `ybc_att` |
| `load_pfr_advstats(stat_type='pass')` | S016 `int_team_line_quality` | `pressure_pct`, `times_blitzed`, `pocket_time` |
| `load_team_stats` | S016 `int_team_environment` | pace, EPA — 136 cols, select on ingest, don't carry all of them |
| `load_draft_picks` | S016 `int_player_role` | rookie draft capital |
| `load_depth_charts(2026)` | S016 `int_player_role` | `pos_rank`, `pos_slot` |
| `load_schedules(2026)` | S016 `int_team_environment` | Vegas lines; 112/272 games priced today, all 32 teams covered, median 7 games/team |
| `load_ff_opportunity` | S016 `int_player_efficiency_priors` | `*_exp` columns |
| `load_snap_counts` | S016 `int_player_role` + S008 (backlog) | `offense_pct` |

Plus, sample-scale only for now since no S016/S018 feature consumes them yet but S008
will: `load_pbp`, `load_rosters_weekly`, `load_injuries`.

### Non-`nflreadpy` ADP ingest (2 new modules)
- **ESPN ADP** — `src/nfl/ingest/adp_espn.py`. Free JSON, no auth,
  `ownership.averageDraftPosition`. **Live/current-season only** — the 2025 historical
  pull returns a constant `170.0` sentinel for every player and must not be trusted.
  Ingest current season only; add a test that rejects a column of identical values so
  this failure mode can't silently reappear.
- **FFC ADP** — `src/nfl/ingest/adp_ffc.py`. Free JSON, no key, no tier. Real multi-season
  history (2022/2024/2025 verified, 8,162 drafts in 2026 alone). Pull the full available
  window, same pattern as `player_stats`'s season window.

Both are the market/consensus feed S016 measures ECR against — ESPN because it's the
market James actually drafts in, FFC because it's the only trustworthy multi-season ADP
for S017's backtest.

### Snapshotting (new capability)
- `ff_rankings` and ESPN ADP are **live snapshots with no vendor-side history** — today's
  pull overwrites yesterday's. Every ingest run must append a dated row set
  (`snapshot_date` column, or a dated partition) instead of overwriting, so S017 has
  something to backtest ECR/live-ADP against starting from 2026 rather than never.
- FFC ADP does **not** need this — the vendor already serves historical drafts by season.

## Acceptance Criteria

### Implementation — PR 1 (`s007-ingest-widening`, 2026-08-30)
- [x] `src/nfl/ingest/pfr_advstats.py` — rush + pass, both stat types, one module
- [x] `src/nfl/ingest/team_stats.py`
- [x] `src/nfl/ingest/draft_picks.py` — defaults to every draft class (`seasons=True`),
      not the recent history window, since a board veteran's draft year can predate it
- [x] `src/nfl/ingest/depth_charts.py` — defaults to `current_season` (2026) only
- [x] `src/nfl/ingest/schedules.py` extended to also pull `current_season` by default
      (was `history_start_season`..`default_season` only, per S003A's window)
- [x] `src/nfl/ingest/ff_opportunity.py`
- [x] `src/nfl/ingest/snap_counts.py`
- [x] new `Settings.current_season` (default 2026) — distinct from `default_season`
      (most recent *complete* season); used by `depth_charts`/`schedules`
- [x] all new modules match the existing `player_stats.py` shape: runnable as
      `python -m nfl.ingest.<name> [--season ...]`, `ingested_at`/`source` metadata columns

### Implementation — PR 2 (`s007-ingest-widening-pr2`, 2026-08-30)
- [x] `src/nfl/ingest/pbp.py`, `rosters_weekly.py`, `injuries.py` — S008 inputs
- [x] `src/nfl/ingest/adp_espn.py` — current season only, no historical pull attempted;
      rejects a constant `adp` column (the known 2025-sentinel shape) instead of
      silently ingesting it
- [x] `src/nfl/ingest/adp_ffc.py` — full available history + upcoming season, one
      `requests` call per season (the API takes a single `year`, unlike nflreadpy)
- [x] `_common.append_snapshot_parquet` — new shared helper: reads-concats-dedupes-writes
      a Parquet history stamped with `snapshot_date`, so a rerun never erases a prior one
- [x] `ff_rankings.py` wired to it **additively**: `ff_rankings.parquet` (S004/S005A's
      existing source) stays an untouched full-refresh overwrite; a new, separate
      `ff_rankings_snapshots.parquet` accumulates history alongside it. Deliberately not
      one flat-file swap — changing the file S004's already-shipped `stg_nfl__ff_rankings`
      reads would risk breaking the live draft board days before the 2026-09-05 draft.
- [x] new direct dependency `requests>=2.31` in `pyproject.toml` (was only a transitive
      dep via `nflreadpy`; the two new ADP modules import it directly)

### Scope cut from the original AC list — samples deferred to S016/S008
`data/samples/` slices + `scripts/make_samples.py` updates are **not** in this PR (or
PR 1). A sample exists to let CI build a dbt source against a tiny fixture; per this
story's own Definition of Done, **no dbt source is wired for any S007 output yet** —
that happens in S016/S008 when each source actually gets consumed. Committing samples
now would be dead weight with nothing in CI to exercise them, and `make_samples.py`'s
per-source filtering logic (team/week slices for stats-shaped data, name-matched
+ extras for board-shaped data, "a couple of full games, not a token filter" for `pbp`)
is easiest to get right at the same time the corresponding staging model is written,
when the join keys and grain are concretely in front of whoever's writing it. Whichever
of S016/S008 wires a given source's `raw_nfl` entry does its sample slice as part of
that same PR.

### Validation — unit / structural
- [x] unit tests per PR-1 module: schema/dtypes as expected, metadata columns present,
      writes Parquet (fixture/mock, no network in CI — same pattern as existing ingest
      tests); 76 tests green, ruff + mypy --strict clean
- [x] full pull runs clean end-to-end for every PR-1 module against live sources at least
      once — row counts: `team_stats` 570, `snap_counts` 26,612, `draft_picks` 257,
      `depth_charts` 485,277, `pfr_advstats` rush 2,355 / pass 684, `ff_opportunity` 6,054,
      `schedules` (2025+2026) 557 — all on 2025 (or 2026 where applicable) alone
- [x] explicit test: ESPN ADP ingest rejects a column of identical values (the known
      2025-sentinel failure mode) rather than silently ingesting it
- [x] explicit test: two sequential snapshot runs on different dates both survive in the
      output — an append does not clobber the prior run's rows; a same-day rerun with
      identical rows does not double the history
- [x] PR-2 unit tests: 17 new tests (adp_espn, adp_ffc, pbp, rosters_weekly, injuries,
      snapshot helper + ff_rankings integration) — 93 total, all green, ruff +
      mypy --strict clean
- [ ] PR-2 modules get their own live end-to-end pull + row counts before merge

## Definition of Done
Every loader S016 and S008 depend on is pulling clean Parquet locally, with samples
committed for CI and unit tests green (no network). ESPN ADP and `ff_rankings` are
snapshotting dated history starting now, not retroactively. Nothing here defines a dbt
source or model yet — wiring `raw_nfl` sources for these is part of S016/S008 when each
consumes them, following S004's `_nfl__sources.yml` pattern.
