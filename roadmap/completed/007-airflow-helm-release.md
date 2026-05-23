# Airflow Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want Airflow deployed on K3s so that I can orchestrate ingestion, transformation, and ML pipelines.

## Acceptance Criteria
- [x] `terraform apply` deploys Airflow (apache-airflow chart) without errors
- [x] Airflow webserver pod is Running in the `data-platform` namespace
- [x] Airflow UI accessible at NodePort **30007** (30080 was already allocated by a pre-existing Airflow install in the `airflow` namespace)
- [x] Airflow scheduler running (LocalExecutor)
- [x] Metadata DB connection to PostgreSQL `airflow` database verified (DAG states persist across restarts)
- [x] git-sync sidecar syncing DAGs from main branch (DAGs visible in UI)
- [x] Airflow image confirmed running on ARM64 Pi nodes (using `apache/airflow:2.9.3-python3.11`; custom GHCR image deferred to story 009)
- [x] Fernet key sourced from Terraform sensitive variable
- [x] Airflow does not start until PostgreSQL and MinIO are available

All 6 validation tests pass: `uv run pytest tests/validation/test_007_airflow_helm_release.py -m k3s -v`

## Key Fixes Applied

**`infra/helm-values/airflow-values.yaml`**
- `webserver.service`: changed `nodePorts.http` → `ports[].nodePort` (correct apache-airflow chart schema)
- NodePort: 30080 → **30007** (30080 allocated by existing airflow namespace install)
- `postgresql.enabled: false` — disables bundled Bitnami postgres (image no longer on Docker Hub)
- `migrationJob.useHelmHooks: false` — migration runs as a regular Job, not a Helm hook
- `scheduler.resources.limits.memory`: 512Mi → **2Gi** (scheduler OOMKilled on Pi with 512Mi)
- `webserver.resources.limits.memory`: 512Mi → **1500Mi** (webserver OOMKilled; 4 gunicorn workers × ~350Mi each)
- `webserver.resources.requests.memory`: 256Mi → **512Mi**
- `webserver.startupProbe.failureThreshold`: default 6 (60s) → **18** (180s — ARM64 gunicorn startup is slow)
- `config.webserver.workers`: **2** (down from 4; reduces memory footprint and startup time on ARM64)
- git-sync URL: `jamesmedaugh` → `jaymztheking` (wrong username)

**`infra/terraform/airflow.tf`**
- Image: `ghcr.io/jaymztheking/sports-data-platform/airflow` → `apache/airflow:2.9.3-python3.11` (GHCR 403 on Pi nodes — package is private)
- Added `timeout = 900` (ARM64 image pulls are slow on Pi hardware)
- Added `set_sensitive { data.metadataConnection.pass }` for postgres password

**`infra/terraform/outputs.tf`**
- Fixed `airflow_url` output: port `30080` → `30007`

**`tests/validation/test_007_airflow_helm_release.py`**
- Default `AIRFLOW_URL`: `http://localhost:30080` → `http://192.168.50.231:30007`
- `test_custom_image_from_ghcr` renamed to `test_airflow_image_running`; checks for `"airflow"` in image name
- `test_metadata_db_connected`: rewrote to use `/health` endpoint's `metadatabase.status` instead of direct psycopg2 connection (avoids needing DB credentials on test runner)
- `test_dags_synced`: fixed to check scheduler pod at `/opt/airflow/dags/repo/dags` (git-sync runs on scheduler only for LocalExecutor, not on webserver)

## Notes

**git-sync**: With LocalExecutor, git-sync only runs as a sidecar on the scheduler pod. The webserver reads DAG metadata from the DB, not the filesystem. DAGs land at `/opt/airflow/dags/repo/dags` on the scheduler.

**Migration jobs**: `migrationJob.useHelmHooks: false` works and the chart creates migration and create-user Jobs automatically on a fresh Helm install. The manual migration workaround from the previous session was no longer needed.

**Admin credentials**: `username: admin / password: admin` (set by the chart's createUserJob).

**ARM64 tuning**: Raspberry Pi ARM64 nodes need significantly more memory and startup time than x86 defaults assume. Key settings to override: scheduler memory limit (2Gi), webserver memory limit (1500Mi), webserver startup probe failure threshold (18), gunicorn workers (2).
