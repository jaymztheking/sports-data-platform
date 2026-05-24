# Custom Docker Images

**Phase**: 1 — Infrastructure
**Story Points**: 5

## User Story
As a platform engineer, I want custom Docker images for Airflow, Spark, MLflow, and ingestion built for ARM64 and pushed to GHCR so that K3s on Raspberry Pi can pull and run them.

## Acceptance Criteria
- [ ] Airflow image built for linux/arm64, pushed to GHCR, and starts successfully on Pi nodes
- [ ] Spark image (with Iceberg runtime and AWS SDK JARs) built for linux/arm64, pushed to GHCR, and starts successfully on Pi nodes
- [ ] `spark-defaults.conf` pre-configures Iceberg catalog, S3 endpoints, and MinIO credentials; configuration confirmed active at runtime
- [ ] MLflow image (with mlflow, psycopg2-binary, boto3) built for linux/arm64, pushed to GHCR, and starts successfully on Pi nodes
- [ ] Ingestion image built for linux/arm64, pushed to GHCR, and starts successfully on Pi nodes
- [ ] `tabulario/iceberg-rest:1.5.0` verified for ARM64; built from source if upstream image lacks ARM64 support
