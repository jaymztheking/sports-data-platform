# Iceberg REST Catalog Deployment

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want an Iceberg REST catalog running on K3s so that Spark can manage Iceberg tables with a standard catalog interface.

## Acceptance Criteria
- [x] `iceberg.tf` defines `kubernetes_deployment` and `kubernetes_service` resources
- [x] Uses `tabulario/iceberg-rest:1.5.0` image
- [x] Configured to use S3FileIO pointing to MinIO
- [x] Warehouse path set to `s3://spark-warehouse/`
- [x] AWS credentials reference MinIO secret
- [x] Resource limits appropriate for Raspberry Pi (256Mi-512Mi)
- [x] Depends on MinIO deployment
