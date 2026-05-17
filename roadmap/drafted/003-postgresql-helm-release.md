# PostgreSQL Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a platform engineer, I want PostgreSQL deployed via Helm on K3s so that it serves as the metadata store (Airflow, MLflow) and the silver/gold serving layer.

## Acceptance Criteria
- [x] `postgres.tf` defines a `helm_release` using bitnami/postgresql chart
- [x] Init SQL script creates databases: `airflow`, `mlflow`
- [x] Init SQL script creates schemas: `raw_mlb`, `raw_nfl`, `raw_nba`, `raw_nhl`, `staging`, `marts`
- [x] ConfigMap mounts the init script
- [x] Helm values set ARM64-appropriate resource limits (256Mi-512Mi)
- [x] Persistence enabled (5Gi)
- [x] Password injected via Terraform sensitive variable
