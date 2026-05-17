# MLflow Tracking Server Deployment

**Phase**: 1 — Infrastructure
**Story Points**: 2

## User Story
As a data scientist, I want MLflow deployed on K3s so that I can track experiments, log metrics, and store model artifacts.

## Acceptance Criteria
- [x] `mlflow.tf` defines `kubernetes_deployment` and `kubernetes_service` resources
- [x] Custom MLflow image with psycopg2 and boto3
- [x] Backend store URI points to PostgreSQL mlflow database
- [x] Artifact root points to MinIO `mlflow-artifacts` bucket
- [x] Exposed via NodePort (30500)
- [x] Resource limits appropriate for Pi (256Mi-512Mi)
- [x] Depends on PostgreSQL and MinIO
