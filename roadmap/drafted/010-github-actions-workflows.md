# GitHub Actions CI/CD Workflows

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a developer, I want CI/CD pipelines so that code is automatically linted, tested, and deployed to K3s on push.

## Acceptance Criteria
- [x] CI workflow runs on PRs and pushes to main
- [x] CI jobs: lint (ruff + mypy), test (pytest), dbt (compile against service container Postgres)
- [x] Deploy workflow triggers on push to main when `infra/` or `docker/` change
- [x] Deploy builds ARM64 images via matrix strategy and pushes to GHCR
- [x] Deploy runs `terraform init`, `plan`, `apply` with secrets as TF_VAR inputs
- [x] Both workflows use appropriate runners (ubuntu-latest for CI, self-hosted for deploy)
