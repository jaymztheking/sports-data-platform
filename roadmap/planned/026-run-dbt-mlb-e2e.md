# Run dbt MLB Models End-to-End

**Phase**: 3 — Silver & Gold Layers
**Story Points**: 3

## User Story
As a data engineer, I want to run `dbt build --select tag:mlb` against real data so that staging views and mart tables are validated in PostgreSQL.

## Acceptance Criteria
- [ ] `dbt deps` installs dbt-utils
- [ ] `dbt run --select tag:mlb,tag:staging` creates staging views in `staging` schema
- [ ] `dbt run --select tag:mlb,tag:marts` creates mart tables in `marts` schema
- [ ] `dbt test --select tag:mlb` passes all not_null and unique tests
- [ ] `dbt seed` loads `mlb_teams.csv` into the warehouse
- [ ] Gold tables queryable with expected data (e.g., batting leaders, pitching stats)
