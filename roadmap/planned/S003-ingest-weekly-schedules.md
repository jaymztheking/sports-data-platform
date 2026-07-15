# S003 — Ingest: nflreadpy weekly + schedules → Parquet

**Phase**: 1 — Thin vertical slice
**Functional unit**: `nflreadpy` → `data/raw/{weekly,schedules}.parquet`

## User Story
As an analyst, I want weekly player stats and schedules pulled locally as Parquet so
that dbt has real NFL data to model.

## Scope
Hand-coded Python ingestion (James writes the core; Claude scaffolds stubs/tests).
Two modules to start: weekly player stats and schedules. Adds `ingested_at`/`source`
metadata columns. Also emits a tiny slice into `data/samples/` for CI.

## Acceptance Criteria

### Implementation
- [ ] `src/nfl/config.py` — pydantic-settings (paths, default season)
- [ ] `src/nfl/ingest/weekly.py`, `src/nfl/ingest/schedules.py` — pull via `nflreadpy`, write Parquet, add metadata cols
- [ ] runnable as `python -m nfl.ingest.weekly --season <yr>`
- [ ] committed `data/samples/{weekly,schedules}.parquet` (small: ~2 teams / few weeks)

### Validation — unit / structural
- [ ] unit tests: metadata columns present, schema/dtypes as expected, writes Parquet (use a fixture/mock, no network in CI)

## Definition of Done
Ingest modules produce Parquet locally; unit tests green in CI; sample committed.
