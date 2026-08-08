# S005 — fct_player_week (first fantasy product)

**Phase**: 1 — Thin vertical slice
**Functional unit**: staging → `fct_player_week` mart (contracted)

## User Story
As a fantasy manager, I want per-player weekly fantasy points (configurable scoring)
plus volume metrics so that I can evaluate players.

## Scope
The first tangible product. James hand-writes the scoring SQL; Claude scaffolds the
contract YAML + one reference dbt unit test. Scoring configurable via a seed.

**Bounded by S003's data.** This mart is built solely on `stg_nfl__player_stats` +
`stg_nfl__schedules`. Snap % needs `load_snap_counts` and red-zone touches need
`load_pbp` — neither is ingested until **S007**, so both moved to **S008**, where the
usage intermediates live. Keeping them out is what makes this a thin vertical slice.

## Acceptance Criteria

### Implementation
- [ ] `seeds/scoring_rules.csv` — PPR / half / standard weights
- [ ] `models/marts/nfl/fct_player_week.sql` — points + the volume metrics weekly player
      stats carries: targets, carries, receiving air yards, target share, air-yards share
      (snap % and red-zone touches are **not** here — see Scope)
- [ ] `_nfl__marts.yml` — `contract: {enforced: true}` with portable `data_type`s + tests
- [ ] `dbt` **unit test(s)** on the scoring math (fixed inputs → known points)

### Validation — unit / structural
- [ ] `dbt build --target dev` (`NFL_DUCKDB_PATH=:memory:`, the CI path) builds the mart, contract holds, generic + unit tests pass
- [ ] `dbt_expectations` range check on points

## Definition of Done
`fct_player_week` builds under an enforced contract on `ci`; scoring unit tests green.
