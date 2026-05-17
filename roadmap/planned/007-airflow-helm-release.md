# Airflow Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want Airflow deployed on K3s so that I can orchestrate ingestion, transformation, and ML pipelines.

## Acceptance Criteria
- [ ] `terraform apply` deploys Airflow (apache-airflow chart) without errors
- [ ] Airflow webserver pod is Running in the `data-platform` namespace
- [ ] Airflow UI accessible at NodePort 30080
- [ ] Airflow scheduler running (LocalExecutor)
- [ ] Metadata DB connection to PostgreSQL `airflow` database verified (DAG states persist across restarts)
- [ ] git-sync sidecar syncing DAGs from main branch (DAGs visible in UI)
- [ ] Custom Airflow image (with project ingestion dependencies) confirmed running on ARM64 Pi nodes
- [ ] Fernet key sourced from Terraform sensitive variable
- [ ] Airflow does not start until PostgreSQL and MinIO are available
