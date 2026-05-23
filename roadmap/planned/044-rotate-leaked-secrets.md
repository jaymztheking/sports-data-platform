# Rotate Leaked Secrets

**Phase**: 1 — Infrastructure
**Story Points**: 1

## User Story

As a platform operator, I want all credentials that were accidentally pushed to GitHub rotated so that the exposure window is closed.

## Background

Commit `7a02829` (2026-05-23) accidentally included Terraform state backup files:
- `infra/terraform/terraform.tfstate.1779553435.backup`
- `infra/terraform/terraform.tfstate.1779555028.backup`
- `infra/terraform/terraform.tfstate.1779556135.backup`
- `infra/terraform/.terraform.tfstate.lock.info`

These files contained plaintext secrets from `terraform.tfvars`. Commit `d5cab2d` immediately removed them, but the values exist in GitHub history for the window between the two pushes.

## Credentials to Rotate

| Secret | Where Used | Current Value (do not reuse) |
|--------|-----------|-------------------------------|
| `postgres_password` | Bitnami PostgreSQL Helm release, Airflow metadata connection, MLflow DB URL | was `!VE@3t79n^Pkkf8UoyXPE1T%` |
| `minio_root_password` | MinIO Helm release | was `!qtVSpd&vQlIBJXLEz2#@&gR` |
| `airflow_fernet_key` | Airflow Fernet encryption | was `0omacW5Xy7N1ZtcCOJoPuuyBIGwJEXHyfa7p1zDwOzM=` |

## Acceptance Criteria

- [ ] New `postgres_password` generated and updated in: PostgreSQL Helm release (`auth.postgresPassword`), Airflow `data.metadataConnection.pass`, MLflow DB connection URL, `terraform.tfvars`
- [ ] New `minio_root_password` generated and updated in: MinIO Helm release, `terraform.tfvars`
- [ ] New `airflow_fernet_key` generated and updated in: Airflow Helm release, `terraform.tfvars`
- [ ] `terraform apply` completes without errors after rotation
- [ ] All services still healthy after rotation (PostgreSQL, MinIO, Airflow, MLflow)
- [ ] Old credentials no longer work

## Implementation Notes

Generate new secrets locally (never in CI):
```bash
# Postgres password
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24)))"

# MinIO password (same)
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24)))"

# Airflow fernet key
python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

Use only alphanumeric characters for passwords to avoid URL-encoding issues in connection strings (learned from this session — special chars in postgres password caused issues with Airflow's metadata connection URL).

Update `infra/terraform/terraform.tfvars` (gitignored) then run `terraform apply`.

**Warning:** rotating `postgres_password` will cause a brief outage as the PostgreSQL pod restarts. Rotating `airflow_fernet_key` will invalidate any encrypted Airflow connections stored in the DB — re-enter them after rotation.

## Priority

Do before any production data is stored or before the cluster is accessible outside the home network.
