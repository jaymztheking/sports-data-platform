# MinIO Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 2

## User Story
As a platform engineer, I want MinIO deployed via Helm on K3s so that it provides S3-compatible object storage for the bronze layer and MLflow artifacts.

## Acceptance Criteria
- [x] `terraform apply` deploys MinIO (minio/minio) without errors
- [x] MinIO pod is Running in the `data-platform` namespace
- [x] MinIO console accessible at NodePort 30090
- [x] Buckets `bronze`, `mlflow-artifacts`, `spark-warehouse` created and accessible via S3 API
- [x] 10Gi PVC bound and in use
- [x] MinIO root password sourced from Terraform sensitive variable (not hardcoded)
