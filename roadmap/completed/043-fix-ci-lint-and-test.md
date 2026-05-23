# Fix CI: Lint and Test Jobs

**Phase**: 1 — Infrastructure
**Story Points**: 2

## User Story

As a developer, I want the Lint and Test CI jobs to pass on every push so that the pipeline is a reliable signal and not noise I have to ignore.

## Background

After story 006 push, CI shows:
- **dbt**: passing ✓
- **lint**: failing — `ruff check src/ tests/` finds 23 violations
- **test**: failing — `uv run pytest tests/` runs k3s-marked validation tests in GitHub Actions where no cluster exists; kubectl calls fail

`mypy src/` passes locally and in CI.

## Root Causes

### Ruff (23 violations)
Mostly unused imports (F401, auto-fixable) and lines > 100 chars (E501) in validation test files:
- `test_002_terraform_foundation.py` — unused `os`, 1 long line
- `test_003_postgresql_helm_release.py` — unused `.conftest.NAMESPACE`, 1 long line
- `test_004_minio_helm_release.py` — 1 long line
- `test_005_iceberg_rest_catalog.py` — unused import, 1 long line
- `test_009` through `test_021` — long lines, a few unused imports

### Pytest k3s tests in CI
`pytest tests/` collects all tests including those marked `k3s`. These require a live K3s cluster and a valid `~/.kube/config`. GitHub Actions runners have neither, so they error on the first `kubectl` call.

## Acceptance Criteria

- [x] `uv run ruff check src/ tests/` exits 0 (no violations)
- [x] `uv run pytest tests/` exits 0 in a clean environment with no kubeconfig (k3s tests excluded or skipped)
- [x] CI lint and test jobs both show green on the next push
- [x] k3s validation tests are still runnable locally with `pytest -m k3s`

## Implementation Notes

**Lint fix** — run `uv run ruff check --fix src/ tests/` to auto-resolve F401. Manually wrap remaining E501 lines.

**Test fix** — two options:
1. Change CI workflow `pytest tests/` → `pytest tests/ -m "not k3s"` (simplest; keeps the workflow as the gatekeeper)
2. Add `addopts = "-m 'not k3s'"` to `[tool.pytest.ini_options]` in `pyproject.toml` (applies everywhere — risks hiding k3s tests by default, not recommended)

Preferred: option 1. Also consider splitting the test job into `unit` and `validation` steps so the intent is explicit in the workflow.
