# Integration Tests

**Phase**: 6 — CI/CD and Polish
**Story Points**: 5

## User Story
As a developer, I want integration tests that validate key data flows so that regressions are caught before deployment.

## Acceptance Criteria
- [ ] Test Spark session creation against a local or test Iceberg catalog
- [ ] Test Iceberg-to-Postgres loader writes expected rows
- [ ] Test dbt models compile and run against test Postgres with sample data
- [ ] Test MLflow experiment logging against a local tracking server
- [ ] Tests run in CI with appropriate service containers
