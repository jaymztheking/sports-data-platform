# Terraform Foundation

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a platform engineer, I want Terraform provider configs and variable definitions so that I can manage K3s infrastructure declaratively.

## Acceptance Criteria
- [x] `versions.tf` pins Helm and Kubernetes provider versions
- [x] `main.tf` configures Helm and Kubernetes providers with kubeconfig
- [x] `main.tf` creates the `data-platform` namespace
- [x] `variables.tf` defines all configurable inputs (kubeconfig path, namespace, passwords, image tags)
- [x] Sensitive variables marked with `sensitive = true`
- [x] `outputs.tf` exposes service URLs (Airflow, MinIO, MLflow)
