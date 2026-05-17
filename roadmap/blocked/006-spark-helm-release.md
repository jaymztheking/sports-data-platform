# Spark Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want Spark master and workers deployed on K3s so that ingestion jobs can run PySpark against Iceberg tables.

## Acceptance Criteria
- [ ] `terraform apply` deploys Spark (bitnami/spark) without errors
- [ ] Spark master pod and 2 worker pods are Running in the `data-platform` namespace
- [ ] Spark UI shows master and both workers connected
- [ ] Custom Spark image (with Iceberg JARs and AWS SDK) confirmed running on ARM64 Pi nodes
- [ ] Worker resources within Pi constraints (512Mi request / 1Gi limit)
- [ ] Spark does not start until MinIO and Iceberg REST catalog are available
