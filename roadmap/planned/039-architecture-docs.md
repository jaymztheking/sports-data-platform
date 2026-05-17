# Architecture Documentation

**Phase**: 6 — CI/CD and Polish
**Story Points**: 3

## User Story
As a portfolio reviewer, I want detailed architecture documentation with diagrams so that I can understand the platform's design decisions and data flows.

## Acceptance Criteria
- [ ] `docs/architecture.md` with Mermaid diagrams showing data flow, service topology, and medallion layers
- [ ] Explanation of key design decisions (why Iceberg, why REST catalog, why dbt on Postgres)
- [ ] Diagram of K3s cluster layout across 6 Raspberry Pis
- [ ] Description of data mesh domain separation pattern
