# S001 — Foundation: repo reset + tooling + docs + roadmap

**Phase**: 0 — Foundation
**Functional unit**: a clean, CI-green repo skeleton for the NFL platform

## User Story
As the developer, I want a clean foundation (deps, docs, roadmap, lint/type/test gate)
so that every later story builds on a cohesive base instead of the old torn-down stack.

## Scope
Repo reset only — no data, no dbt models yet. Establishes tooling and conventions.

## Acceptance Criteria

### Implementation
- [ ] `pyproject.toml` rewritten: uv, `nflreadpy`/`polars`/`duckdb`, dbt + sqlfluff extras, dev extras; old Spark/Iceberg/MLB deps removed
- [ ] `CLAUDE.md`, `HANDOFF.md`, `README.md` describe the light architecture + collaboration protocol
- [ ] `roadmap/` swim lanes populated (S001 active; S002–S006 planned; S007–S015 backlog)
- [ ] `.claude/agents/{scrum-master,test-writer}.md` adapted to the new lanes/stack
- [ ] `.env.example` and `.gitignore` updated for DuckDB/dbt/Postgres-prod (no MinIO/Spark)
- [ ] `src/nfl/` package skeleton + `tests/` placeholder

### Validation — unit / structural
- [ ] `uv lock` resolves; `uv sync --extra dev --extra dbt` succeeds
- [ ] `ruff check src/ tests/`, `mypy src/`, `pytest tests/ -m "not k3s"` all pass
- [ ] PR opened against `main`; CI green

## Definition of Done
Lint/type/test gate green locally and in CI on the S001 PR.
