# dbt Project Setup

**Phase**: 3 — Silver & Gold Layers
**Story Points**: 2

## User Story
As a data engineer, I want a dbt project configured for PostgreSQL so that I can build transformation models across sport domains.

## Acceptance Criteria
- [x] `dbt_project.yml` configures staging as views, marts as tables, with schema routing per layer
- [x] `profiles.yml` connects to PostgreSQL via environment variables
- [x] `packages.yml` includes dbt-utils
- [x] Model tags set per sport and layer (e.g., `mlb`, `staging`, `marts`)
