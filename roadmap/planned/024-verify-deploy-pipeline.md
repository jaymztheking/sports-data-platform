# Verify GitHub Actions Deploy Pipeline

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a developer, I want the deploy pipeline to run end-to-end on push so that infrastructure changes are automatically applied to the cluster.

## Acceptance Criteria
- [ ] Self-hosted runner on Pi is registered and online
- [ ] Push to `main` changing `infra/` or `docker/` triggers deploy workflow
- [ ] Image build job completes and images appear in GHCR
- [ ] Terraform plan and apply jobs complete successfully
- [ ] GitHub secrets configured (POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD, AIRFLOW_FERNET_KEY)
