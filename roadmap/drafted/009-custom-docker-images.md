# Custom Docker Images

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a platform engineer, I want custom Docker images for Airflow, Spark, MLflow, and ingestion so that each service has the correct dependencies and configurations for ARM64.

## Acceptance Criteria
- [x] Airflow Dockerfile extends official image with project ingestion dependencies via uv
- [x] Spark Dockerfile extends bitnami/spark with Iceberg runtime and AWS SDK JARs
- [x] `spark-defaults.conf` pre-configures Iceberg catalog, S3 endpoints, and MinIO credentials
- [x] MLflow Dockerfile installs mlflow, psycopg2-binary, boto3 with shell-form CMD for env var expansion
- [x] Ingestion Dockerfile installs project with ingestion extras and copies src
