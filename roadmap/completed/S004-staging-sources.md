# S004 — Staging + sources (cross-adapter)

**Phase**: 1 — Thin vertical slice
**Functional unit**: raw Parquet/tables → `stg_nfl__player_stats`, `stg_nfl__schedules`

## User Story
As an analyst, I want cleaned, typed staging views so that marts build on stable inputs.

## Scope
Define `raw_nfl` sources once, resolving in both engines (DuckDB `external_location`
meta over Parquet; real tables in Postgres). Staging SQL is engine-agnostic. James
hand-writes the staging SQL; Claude scaffolds `_nfl__sources.yml` + one reference model.

## Acceptance Criteria

### Implementation
- [x] `models/staging/nfl/_nfl__sources.yml` — `raw_nfl` sources w/ freshness + `external_location` meta for DuckDB
- [x] `stg_nfl__player_stats.sql`, `stg_nfl__schedules.sql`, **`stg_nfl__ff_rankings.sql`** — typed/renamed/cleaned views
- [x] `_nfl__staging.yml` — column tests (not_null/unique on keys)
- [x] `macros/normalize_player_name.sql` — the stats↔board join key, defined once
- [x] `.sqlfluff` — dbt templater config (none existed); `sqlfluff lint` is clean

### Validation — unit / structural
- [x] `dbt build --target dev` on sample data (`NFL_DUCKDB_PATH=:memory:`, the CI path): 22/22 pass
- [x] same build on the **full** season in `data/raw`: 22/22 pass
- [x] `dbt source freshness` passes on all three sources

## Definition of Done
Staging views build and pass tests on the CI sample; sources resolve on DuckDB. ✅

## What building it turned up

Three things the sample slice could not have shown — all found by also building against
the full season, which is why that step is now an AC:

1. **22 identity-less rows.** `player_stats` carries ~one row per team-week with null
   `player_id`, null name, null position and 0.0 points — nflverse placeholders. Staging
   filters them; they were the only source of nulls in the grain key.
2. **Generational suffixes broke the join.** The board writes `Patrick Mahomes II` /
   `Travis Etienne Jr.`; nflverse writes neither. Unstripped, **four of the top-60 2025
   PPR scorers** (Mahomes, James Cook, Etienne, Pitts) silently fell off the draft board —
   failing as "not ranked" rather than as an error. `normalize_player_name` strips them.
   Match rate after: **100% of the top-100** producers, 97% of the top-200.
3. **Name+position is not unique.** Two distinct WRs named *Isaiah Williams* sit on the
   2026 board (ffverse 26379 @NYJ, 10977 @FA). Staging keeps both and grains on
   `ff_player_id`; **S005A must resolve the collision at join time** — it is the one
   place the draft board can still silently pick the wrong player.

The committed sample was also regenerated so the two sample files overlap on 30 players,
otherwise a broken join would pass CI against a slice with no matching rows.
