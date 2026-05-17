# SQL Linting with sqlfluff

**Phase**: 6 — CI/CD and Polish
**Story Points**: 2

## User Story
As a developer, I want SQL models linted by sqlfluff so that dbt code follows consistent style conventions.

## Acceptance Criteria
- [ ] `.sqlfluff` config file with dialect set to postgres and project conventions
- [ ] All existing dbt models pass sqlfluff lint (or have intentional exclusions)
- [ ] sqlfluff step added to CI workflow
- [ ] Makefile target `make sql-lint` for local use
