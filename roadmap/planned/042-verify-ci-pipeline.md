# Verify CI Pipeline End-to-End

**Phase**: 6 — CI/CD and Polish
**Story Points**: 2

## User Story
As a developer, I want the CI pipeline to pass on a clean PR so that I have confidence in automated quality gates.

## Acceptance Criteria
- [ ] Lint job passes (ruff + mypy clean)
- [ ] Test job passes (all pytest tests green)
- [ ] dbt job passes (compile succeeds against service container Postgres)
- [ ] sqlfluff job passes (all SQL models clean)
- [ ] CI runs in under 5 minutes
