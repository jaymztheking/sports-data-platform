# Iceberg REST Catalog Deployment

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want an Iceberg REST catalog running on K3s so that Spark can manage Iceberg tables with a standard catalog interface.

## Acceptance Criteria
- [x] `terraform apply` deploys the Iceberg REST catalog (tabulario/iceberg-rest:1.5.0) without errors
- [x] Iceberg REST catalog pod is Running in the `data-platform` namespace
- [x] Catalog HTTP endpoint responds (GET /v1/config returns 200)
- [x] Catalog uses S3FileIO pointing to MinIO with warehouse at `s3://spark-warehouse/`
- [x] `tabulario/iceberg-rest:1.5.0` image confirmed running on ARM64 Pi nodes (built from source if upstream image lacks ARM64 support)
- [x] Resource limits within Pi constraints (256Mi request / 512Mi limit)
- [x] Catalog does not start until MinIO is available (dependency enforced)
