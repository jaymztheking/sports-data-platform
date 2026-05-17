# MLB Intermediate dbt Models

**Phase**: 3 — Silver & Gold Layers
**Story Points**: 3

## User Story
As a data engineer, I want intermediate dbt models for MLB so that complex transformations are broken into testable steps before reaching the marts.

## Acceptance Criteria
- [ ] Create `models/intermediate/mlb/` directory
- [ ] Build intermediate model joining statcast pitch data with player dimensions
- [ ] Build intermediate model aggregating statcast data to game-level stats
- [ ] Intermediate models materialized as views in `staging` schema
- [ ] Downstream mart models updated to reference intermediate layer where appropriate
