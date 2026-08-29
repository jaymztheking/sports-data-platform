# S005A — fct_player_season (draft board)

**Phase**: 1 — Thin vertical slice
**Functional unit**: staging → `fct_player_season` mart (contracted)

> **Why this exists.** Added 2026-08-28 for the 2026-09-05 draft. `S005 fct_player_week`
> is the wrong grain for draft prep: on draft day the 2026 season has not kicked off, so
> there are zero 2026 weekly rows. Draft decisions need *prior-season* season-grain rates
> joined to draft-market cost. `S005` is deferred to post-draft, where it becomes the
> in-season product.

## User Story
As a fantasy manager drafting on 2026-09-05, I want each player's 2025 production
expressed as per-game rates with positional ranks alongside their current consensus
draft rank, so that I can see who is going later than they produce.

## Scope
Season-grain mart over `stg_nfl__player_stats` (aggregated from weekly) joined to
`stg_nfl__ff_rankings` for draft cost. Scoring reuses `seeds/scoring_rules.csv` from S005.

> **Data note (verified 2026-08-28 against a live pull).** `load_ff_rankings` returns
> **no `adp` column** — the cost signal is **`ecr`** (expert consensus rank) plus
> `sd` / `best` / `worst`. ECR is a consensus draft rank, so it substitutes cleanly for
> ADP, but name the columns `ecr*`, not `adp*`. The feed is also **not** a single board:
> 5,552 rows spanning 31 `page_type`s and 9 `ecr_type`s (dynasty, best-ball, superflex,
> redraft). Staging **must filter to `ecr_type = 'ro'`** (redraft overall) or the join
> fans out. `scrape_date` confirms it is the live 2026 board.

Deliberately **out**: snap % and red-zone touches (need `load_snap_counts` / `load_pbp`,
not ingested until S007), projections, and any modelling. This is descriptive.

## Acceptance Criteria

### Implementation
- [ ] `seeds/scoring_rules.csv` — PPR / half / standard weights (shared with S005)
- [ ] `models/marts/nfl/fct_player_season.sql`, grain = player × season × scoring format:
      - games played, total + **per-game** fantasy points
      - volume: targets, carries, receiving air yards
      - shares: target share, air-yards share
      - consistency: stddev of weekly points, floor/ceiling (p25/p75 weekly)
      - `position_rank` (per position, by per-game points)
- [ ] ECR join → `ecr`, `ecr_position_rank`, `ecr_sd`, and **`value_over_ecr`**
      (ECR-implied rank minus production rank; positive = producing better than draft
      cost). Join on normalised name + position — there is no shared player id between
      `player_stats` (`player_id`, gsis) and `ff_rankings` (`id`/`mergename`, ffverse),
      so expect a fuzzy-match step and assert the unmatched rate stays low.
- [ ] `_nfl__marts.yml` — `contract: {enforced: true}`, portable `data_type`s + tests
- [ ] `dbt` **unit test** on the scoring math (fixed inputs → known points)

### Validation — unit / structural
- [ ] `dbt build --target dev` (`NFL_DUCKDB_PATH=:memory:`) builds the mart, contract holds
- [ ] `not_null` / `unique` on the grain key; `dbt_expectations` range check on per-game points
- [ ] spot-check: top-12 RB by per-game 2025 points is not obviously wrong

## Definition of Done
`fct_player_season` builds under an enforced contract, and James can query it to rank
players by value-over-ADP before the 2026-09-05 draft.
