# MLflow Tracking Server Deployment

**Phase**: 1 — Infrastructure
**Story Points**: 2

## User Story
As a data scientist, I want MLflow deployed on K3s so that I can track experiments, log metrics, and store model artifacts.

## Acceptance Criteria
- [x] `terraform apply` deploys MLflow without errors
- [x] MLflow pod is Running in the `data-platform` namespace
- [x] MLflow UI accessible at NodePort 30500
- [x] Experiment runs persist across pod restarts (backend store connected to PostgreSQL `mlflow` database)
- [x] Model artifacts stored in MinIO `mlflow-artifacts` bucket
- [x] Custom MLflow image (with psycopg2 and boto3) confirmed running on ARM64 Pi nodes
- [x] Resource limits within Pi constraints (256Mi request / 512Mi limit)
- [x] MLflow does not start until PostgreSQL and MinIO are available
