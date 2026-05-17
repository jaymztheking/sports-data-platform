# Build and Push ARM64 Docker Images

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a platform engineer, I want ARM64 Docker images built and pushed to GHCR so that K3s on Raspberry Pi can pull and run them.

## Acceptance Criteria
- [ ] Airflow image builds for ARM64 and pushes to GHCR
- [ ] Spark image (with Iceberg JARs) builds for ARM64 and pushes to GHCR
- [ ] MLflow image builds for ARM64 and pushes to GHCR
- [ ] Ingestion image builds for ARM64 and pushes to GHCR
- [ ] All images verified to run on ARM64 Pi nodes
- [ ] `tabulario/iceberg-rest` verified for ARM64 (or built from source if needed)
