# MinIO Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 2

## User Story
As a platform engineer, I want MinIO deployed via Helm on K3s so that it provides S3-compatible object storage for the bronze layer and MLflow artifacts.

## Acceptance Criteria
- [x] `minio.tf` defines a `helm_release` using minio/minio chart
- [x] Helm values configure standalone mode
- [x] Buckets auto-created: `bronze`, `mlflow-artifacts`, `spark-warehouse`
- [x] Console exposed via NodePort (30090)
- [x] Persistence enabled (10Gi)
- [x] Root password injected via Terraform sensitive variable
