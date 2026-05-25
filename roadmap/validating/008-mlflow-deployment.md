# MLflow Tracking Server Deployment

**Phase**: 1 — Infrastructure
**Story Points**: 2

## User Story
As a data scientist, I want MLflow deployed on K3s so that I can track experiments, log metrics, and store model artifacts.

## Acceptance Criteria
- [ ] `terraform apply` deploys MLflow without errors
- [ ] MLflow pod is Running in the `data-platform` namespace
- [ ] MLflow UI accessible at NodePort 30500
- [ ] Experiment runs persist across pod restarts (backend store connected to PostgreSQL `mlflow` database)
- [ ] Model artifacts stored in MinIO `mlflow-artifacts` bucket
- [ ] Custom MLflow image (with psycopg2 and boto3) confirmed running on ARM64 Pi nodes
- [ ] Resource limits within Pi constraints (256Mi request / 512Mi limit)
- [ ] MLflow does not start until PostgreSQL and MinIO are available
