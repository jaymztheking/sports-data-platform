# PostgreSQL Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a platform engineer, I want PostgreSQL deployed via Helm on K3s so that it serves as the metadata store (Airflow, MLflow) and the silver/gold serving layer.

## Acceptance Criteria
- [x] `terraform apply` deploys PostgreSQL (bitnami/postgresql) without errors
- [x] PostgreSQL pod is Running in the `data-platform` namespace
- [x] PostgreSQL accepts connections (verified via psycopg2 or psql)
- [x] Databases `airflow` and `mlflow` exist
- [x] Schemas `raw_mlb`, `raw_nfl`, `raw_nba`, `raw_nhl`, `staging`, `marts` exist in PostgreSQL
- [x] Resource limits set to ARM64-appropriate values (256Mi request / 512Mi limit)
- [x] 5Gi PVC bound and in use
- [x] PostgreSQL password sourced from Terraform sensitive variable (not hardcoded in IaC)
