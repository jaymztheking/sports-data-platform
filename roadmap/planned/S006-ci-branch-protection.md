# S006 — CI + branch protection

**Phase**: 1 — Thin vertical slice
**Functional unit**: PR gate that runs the full stack + protected `main`

## User Story
As the developer, I want every PR to run lint/type/tests + sqlfluff + a full dbt build
on ephemeral DuckDB, and `main` protected, so quality is enforced automatically.

## Scope
Extend `.github/workflows/ci.yml`; configure branch protection on `main`.

## Acceptance Criteria

### Implementation
- [ ] CI jobs: `ruff` + `mypy` + `pytest -m "not k3s"`; `sqlfluff lint`; `dbt deps` + `dbt build --target ci` on `data/samples/`
- [ ] `.pre-commit-config.yaml` gains sqlfluff (dbt templater)
- [ ] branch protection on `main`: require the CI checks + PR review; block direct pushes

### Validation — unit / structural
- [ ] a PR shows all checks running and green
- [ ] a deliberately failing model/test makes CI red (spot check)

## Definition of Done
CI runs the full gate on PRs; `main` is protected and requires green checks.
