# S003A — Multi-season history window

**Phase**: 1 — Thin vertical slice
**Functional unit**: single-season ingest → configurable season window (2022→2025)

> Added 2026-08-28, mid-S004, after measuring what the draft board would actually stand
> on. The answer was **one season** — enough to rank players, not enough to trust the
> ranking.

## User Story
As a fantasy manager, I want several seasons of history behind the draft board so that a
player's rate stats reflect a trend rather than a single outlier year.

## Scope
Widen ingest from one season to a configurable window. Deliberately **not** in scope:
weighting recent seasons more heavily, age curves, or trend features — those are S005A
and beyond. This story only makes the data available.

## Acceptance Criteria

### Implementation
- [x] `config.py` — `history_start_season` (default 2022) + `default_seasons` property;
      widening the window is one env var, not a code change
- [x] `--season` takes `nargs="+"`; bare invocation pulls the whole window
- [x] `schedules.py` gets the same treatment
- [x] `scripts/make_samples.py` keeps **all** seasons in the slice (narrows on teams and
      weeks only) so CI exercises multi-season aggregation

### Validation
- [x] 25 unit tests green, incl. `tests/test_config.py` for the window property
- [x] `dbt build` green on both `data/samples` and the full 4-season `data/raw` (22/22)

## Definition of Done
Ingest pulls 2022–2025; staging builds and tests pass on all of it. ✅

## Result

| | 1 season (before) | 4 seasons (after) |
|---|---|---|
| player-weeks | 18,522 | **75,879** |
| games | 285 | 1,139 |
| avg games behind a top-50 board player | ~14 | **49.4** |
| top-50 with 3+ seasons of history | n/a | 39 of 50 |
| top-100 with no history at all | 4 | **3** |

Raw Parquet is 2.0 MB; the committed sample is 127 KB.

Only **Jeremiyah Love (RB, board rank 41)** sits in the top 60 with no NFL history — a
true rookie, so the blank is correct rather than a coverage failure. S005A should render
such players as unranked-on-production, not as zero.

## Future state (explicitly deferred)
James wants materially more history than 2022. `history_start_season` is the single knob;
nflverse player stats reach back to 1999. Deferred purely on time before the 2026-09-05
draft — revisit once the board ships. Tracked in `roadmap/backlog/`.
