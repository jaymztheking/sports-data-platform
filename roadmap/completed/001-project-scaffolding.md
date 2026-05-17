# Project Scaffolding

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a developer, I want a well-structured Python project with modern tooling so that I can develop, lint, test, and build the platform efficiently.

## Acceptance Criteria
- [x] `pyproject.toml` configured with uv, dependency groups (ingestion, ml, dev, dbt)
- [x] `Makefile` with shortcuts for common tasks (install, lint, test, tf-plan, tf-apply, build-images)
- [x] `.gitignore` covers Python, Terraform, dbt, IDE, and OS artifacts
- [x] `.pre-commit-config.yaml` with ruff and mypy hooks
- [x] `.env.example` documents all required environment variables
- [x] `uv sync` installs base dependencies and generates lockfile
- [x] Project directory structure matches planned layout
- [x] Unit tests pass with `uv run pytest`
