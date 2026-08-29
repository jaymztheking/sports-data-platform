# S007 — Ingest widening: projection inputs + ADP/ECR snapshotting

**Phase**: 2 — Our own projections
**Functional unit**: `nflreadpy` + two new public JSON APIs → Parquet, widening ingest to
cover everything S016's feature marts (and S008's usage intermediates) need

> Promoted out of `roadmap/backlog/S007-S015-later-phases.md` 2026-08-29. **Hard
> dependency: S007 → S016, S007 → S008.** Neither can build without this landing first.

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

### Implementation
- [ ] `src/nfl/ingest/pfr_advstats.py` — rush + pass, both stat types, one module
- [ ] `src/nfl/ingest/team_stats.py`
- [ ] `src/nfl/ingest/draft_picks.py`
- [ ] `src/nfl/ingest/depth_charts.py` — 2026 season
- [ ] `src/nfl/ingest/schedules.py` extended to also pull the 2026 season (currently
      scoped to `history_start_season`..2025 per S003A's window)
- [ ] `src/nfl/ingest/ff_opportunity.py`
- [ ] `src/nfl/ingest/snap_counts.py`, `pbp.py`, `rosters_weekly.py`, `injuries.py` — S008
      inputs; `pbp` gets a real few-game `data/samples/` slice, not a token filter (source
      is ~13 MB/season, 49k rows × 372 cols)
- [ ] `src/nfl/ingest/adp_espn.py` — current season only, no historical pull attempted
- [ ] `src/nfl/ingest/adp_ffc.py` — full available history
- [ ] snapshot mechanism: `ff_rankings` and `adp_espn` ingest runs append a `snapshot_date`
      (or write to a dated partition) instead of overwriting the prior run's output
- [ ] all new modules match the existing `player_stats.py` shape: runnable as
      `python -m nfl.ingest.<name> [--season ...]`, `ingested_at`/`source` metadata columns
- [ ] `data/samples/` slices committed for every new source (small: 2 teams / few weeks,
      except `pbp` which needs a couple of full games)
- [ ] `scripts/make_samples.py` updated to regenerate every new sample slice

### Validation — unit / structural
- [ ] unit tests per module: schema/dtypes as expected, metadata columns present, writes
      Parquet (fixture/mock, no network in CI — same pattern as existing ingest tests)
- [ ] explicit test: ESPN ADP ingest rejects or flags a column of identical values (the
      known 2025-sentinel failure mode) rather than silently ingesting it
- [ ] explicit test: two sequential snapshot runs on different dates both survive in the
      output — an append does not clobber the prior run's rows
- [ ] full pull runs clean end-to-end for every new module against live sources at least
      once (not just the mocked unit tests) — record row counts in the PR description

## Definition of Done
Every loader S016 and S008 depend on is pulling clean Parquet locally, with samples
committed for CI and unit tests green (no network). ESPN ADP and `ff_rankings` are
snapshotting dated history starting now, not retroactively. Nothing here defines a dbt
source or model yet — wiring `raw_nfl` sources for these is part of S016/S008 when each
consumes them, following S004's `_nfl__sources.yml` pattern.
