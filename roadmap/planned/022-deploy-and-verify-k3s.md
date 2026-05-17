# Deploy and Verify K3s Services

**Phase**: 1 — Infrastructure
**Story Points**: 5

## User Story
As a platform engineer, I want to run `terraform apply` and verify all services are healthy on the K3s cluster so that the platform is ready for data pipelines.

## Acceptance Criteria
- [ ] `terraform apply` completes without errors
- [ ] `kubectl get pods -n data-platform` shows all pods Running
- [ ] Airflow UI accessible at NodePort 30080
- [ ] MinIO console accessible at NodePort 30090
- [ ] MLflow UI accessible at NodePort 30500
- [ ] PostgreSQL accepts connections, schemas and databases exist
- [ ] MinIO buckets (bronze, mlflow-artifacts, spark-warehouse) created
- [ ] Spark master and workers visible in Spark UI
