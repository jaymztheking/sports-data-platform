# Airflow Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want Airflow deployed on K3s so that I can orchestrate ingestion, transformation, and ML pipelines.

## Acceptance Criteria
- [x] `airflow.tf` defines a `helm_release` using apache-airflow chart
- [x] LocalExecutor configured
- [x] Custom image reference with project dependencies
- [x] git-sync sidecar for DAGs from main branch
- [x] Webserver exposed via NodePort (30080)
- [x] Metadata connection points to PostgreSQL airflow database
- [x] Environment variables configure Spark and MinIO connections
- [x] Fernet key injected via Terraform sensitive variable
- [x] Depends on PostgreSQL and MinIO
