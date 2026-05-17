# Terraform Foundation

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a platform engineer, I want Terraform provider configs and variable definitions so that I can manage K3s infrastructure declaratively.

## Acceptance Criteria
- [ ] `terraform init` and `terraform plan` complete without errors against the K3s cluster
- [ ] `terraform apply` creates the `data-platform` namespace in K3s
- [ ] Helm and Kubernetes provider versions pinned in `versions.tf`
- [ ] All configurable inputs defined in `variables.tf` (kubeconfig path, namespace, passwords, image tags)
- [ ] Sensitive inputs (passwords, keys) marked `sensitive = true`
- [ ] Service URLs (Airflow, MinIO, MLflow) exposed via `outputs.tf`
