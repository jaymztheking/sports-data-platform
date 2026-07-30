# S005 — fct_player_week (first fantasy product)

**Phase**: 1 — Thin vertical slice
**Functional unit**: staging → `fct_player_week` mart (contracted)

## User Story
As a fantasy manager, I want per-player weekly fantasy points (configurable scoring)
plus volume metrics so that I can evaluate players.

## Scope
The first tangible product. James hand-writes the scoring SQL; Claude scaffolds the
contract YAML + one reference dbt unit test. Scoring configurable via a seed.

## Acceptance Criteria

### Implementation
- [ ] `seeds/scoring_rules.csv` — PPR / half / standard weights
- [ ] `models/marts/nfl/fct_player_week.sql` — points + targets/carries/air-yards/snaps/red-zone touches
- [ ] `_nfl__marts.yml` — `contract: {enforced: true}` with portable `data_type`s + tests
- [ ] `dbt` **unit test(s)** on the scoring math (fixed inputs → known points)

### Validation — unit / structural
- [ ] `dbt build --target dev` (`NFL_DUCKDB_PATH=:memory:`, the CI path) builds the mart, contract holds, generic + unit tests pass
- [ ] `dbt_expectations` range check on points

## Definition of Done
`fct_player_week` builds under an enforced contract on `ci`; scoring unit tests green.
