# GitHub Actions CI/CD Workflows

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a developer, I want CI/CD pipelines so that code is automatically linted, tested, and deployed to K3s on push.

## Acceptance Criteria
- [ ] CI workflow runs on PRs and pushes to main; lint (ruff + mypy), test (pytest), and dbt compile all pass in CI
- [ ] Push to main changing `infra/` or `docker/` triggers the deploy workflow
- [ ] ARM64 image matrix build completes and images appear in GHCR
- [ ] `terraform plan` and `terraform apply` jobs complete successfully in the deploy workflow
- [ ] Self-hosted runner on Pi is registered, online, and accepting jobs
- [ ] GitHub Secrets configured: `POSTGRES_PASSWORD`, `MINIO_ROOT_PASSWORD`, `AIRFLOW_FERNET_KEY`
- [ ] Ubuntu-latest runner used for CI; self-hosted Pi runner used for deploy
