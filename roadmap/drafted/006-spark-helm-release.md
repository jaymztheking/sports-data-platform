# Spark Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want Spark master and workers deployed on K3s so that ingestion jobs can run PySpark against Iceberg tables.

## Acceptance Criteria
- [x] `spark.tf` defines a `helm_release` using bitnami/spark chart
- [x] Custom image reference with Iceberg JARs
- [x] Helm values configure 1 master + 2 workers
- [x] Worker resources tuned for Pi (512Mi-1Gi RAM)
- [x] Depends on MinIO and Iceberg REST catalog
