# Airflow Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want Airflow deployed on K3s so that I can orchestrate ingestion, transformation, and ML pipelines.

## Acceptance Criteria
- [ ] `terraform apply` deploys Airflow (apache-airflow chart) without errors
- [ ] Airflow webserver pod is Running in the `data-platform` namespace
- [ ] Airflow UI accessible at NodePort **30007** (30080 was already allocated by a pre-existing Airflow install in the `airflow` namespace, 147 days old)
- [ ] Airflow scheduler running (LocalExecutor)
- [ ] Metadata DB connection to PostgreSQL `airflow` database verified (DAG states persist across restarts)
- [ ] git-sync sidecar syncing DAGs from main branch (DAGs visible in UI)
- [ ] Airflow image confirmed running on ARM64 Pi nodes (custom GHCR image deferred to story 009 — GHCR packages are private by default; for now using `apache/airflow:2.9.3-python3.11`)
- [ ] Fernet key sourced from Terraform sensitive variable
- [ ] Airflow does not start until PostgreSQL and MinIO are available

## Current State (session ended mid-deployment — 2026-05-23)

Pods are in progress. As of end of session:
- `airflow-statsd`: 1/1 Running ✓
- `airflow-triggerer-0`: 3/3 Running ✓
- `airflow-scheduler-0`: 2/3 Running (scheduler container not yet ready — readiness probe pending)
- `airflow-webserver`: Running but 0/1 (readiness probe pending)

### Fixes applied in this session

**`infra/helm-values/airflow-values.yaml`**
- `webserver.service`: changed `nodePorts.http` → `ports[].nodePort` (correct apache-airflow chart schema)
- NodePort: 30080 → **30007** (30080 allocated by existing airflow namespace install)
- `postgresql.enabled: false` — disables bundled Bitnami postgres (image no longer on Docker Hub)
- `migrationJob.useHelmHooks: false` — migration runs as a regular Job, not a Helm hook
- `scheduler.resources.limits.memory`: 512Mi → **2Gi** (scheduler OOMKilled on Pi with 512Mi)
- git-sync URL: `jamesmedaugh` → `jaymztheking` (wrong username)

**`infra/terraform/airflow.tf`**
- Image: `ghcr.io/jaymztheking/sports-data-platform/airflow` → `apache/airflow:2.9.3-python3.11` (GHCR 403 on Pi nodes — package is private)
- Added `timeout = 900` (ARM64 image pulls are slow on Pi hardware)
- Added `set_sensitive { data.metadataConnection.pass }` for postgres password

**`tests/validation/test_007_airflow_helm_release.py`**
- Default `AIRFLOW_URL`: `http://localhost:30080` → `http://192.168.50.231:30007`
- `test_custom_image_from_ghcr` renamed to `test_airflow_image_running`; checks for `"airflow"` in image name instead of `"ghcr.io"`

### Migration issue
The apache-airflow Helm chart's migration Job (`run-airflow-migrations`) was not being created by Terraform's Helm provider. Worked around by applying a manual one-shot Job:
```
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: airflow-db-migrate-manual
  namespace: data-platform
spec:
  ttlSecondsAfterFinished: 300
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: apache/airflow:2.9.3-python3.11
        command: ["airflow", "db", "migrate"]
        env:
        - name: AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
          valueFrom:
            secretKeyRef:
              name: airflow-metadata
              key: connection
EOF
```
This ran successfully and populated the `alembic_version` table in the `airflow` PostgreSQL DB. The `wait-for-airflow-migrations` init container then passed on the next deploy.

**Note:** if the Helm release is deleted and re-created, this Job must be re-run. Consider investigating why `migrationJob.useHelmHooks: false` doesn't create the Job automatically — may need `createUserJob.useHelmHooks: false` too, or a chart-version-specific config key.

### Remaining work to complete story 007
1. ✅ Scheduler readiness probe — scheduler is **3/3 Running** after memory bump to 2Gi
2. Webserver readiness probe — still pending at session end. Two ReplicaSets cycling (SIGTERM/exit 0, not OOMKill). May need `webserver.readinessProbe.initialDelaySeconds` increased for slow ARM64 gunicorn startup, or just needs time to stabilize. Try adding to values:
   ```yaml
   webserver:
     readinessProbe:
       initialDelaySeconds: 60
   ```
3. Verify Airflow UI at `http://192.168.50.231:30007`
4. Default admin credentials: `username: admin / password: admin` (set by chart)
5. Confirm git-sync is populating `/opt/airflow/dags`
6. Run validation tests: `uv run pytest tests/validation/test_007_airflow_helm_release.py -m k3s -v`
7. Commit + push all changes, move story to `completed/`

### Terraform state note
The Helm release has been cycled several times due to failures. After each failed apply, the state was cleaned with:
```
kubectl delete secret -n data-platform sh.helm.release.v1.airflow.v1
terraform -chdir=infra/terraform state rm helm_release.airflow
```
The apply at session end (task `bdhllvcux`, 900s timeout) was still running. Check its outcome at start of next session. If it's failed/tainted, clean state and re-apply — the DB migration is already done so it should converge quickly.

### Terraform state note
The Helm release has been cycled several times due to failures. After each failed apply, the state was cleaned with:
```
kubectl delete secret -n data-platform sh.helm.release.v1.airflow.v1
terraform -chdir=infra/terraform state rm helm_release.airflow
```
The current apply (background task `bdhllvcux`) was still running at session end with 900s timeout.
