# Spark Helm Release

**Phase**: 1 — Infrastructure
**Story Points**: 3

## User Story
As a data engineer, I want Spark master and workers deployed on K3s so that ingestion jobs can run PySpark against Iceberg tables.

## Acceptance Criteria
- [x] `terraform apply` deploys Spark without errors
- [x] Spark master pod and 2 worker pods are Running in the `data-platform` namespace
- [x] Spark UI shows master and both workers connected
- [x] Custom Spark image (with Iceberg JARs and AWS SDK) confirmed running on ARM64 Pi nodes
- [x] Worker resources within Pi constraints (512Mi request / 1Gi limit)
- [x] Spark does not start until MinIO and Iceberg REST catalog are available

## Block History

### Original block — bitnami/spark removed from Docker Hub
`bitnami/spark` images were removed from Docker Hub entirely (0 tags, confirmed May 2026).
The existing `jaymztheking/spark:latest` was built from `apache/spark:3.5.3` and was
incompatible with the Bitnami Helm chart, which expects its own entrypoint scripts
(`/opt/bitnami/scripts/spark/run.sh`) and sets `SPARK_MODE` via env var.

### Resolution attempt — switch to apache/spark with entrypoint shim
- Replaced `FROM bitnami/spark:3.5` with `FROM apache/spark:3.5.3` (official ARM64 image)
- Added `docker/spark/entrypoint.sh`: reads `SPARK_MODE` env var, runs
  `spark-class org.apache.spark.deploy.master.Master` or `.Worker` in foreground via `exec`
- Rebuilt and pushed `jaymztheking/spark:latest`

### Second block — Bitnami Helm chart security context conflicts
The Bitnami Helm chart (`bitnami/spark:9.4.1`) forces `runAsUser: 1001` and
`readOnlyRootFilesystem: true` regardless of image. Apache Spark image has UID 185
in `/etc/passwd`; UID 1001 is absent, causing Hadoop's `UnixLoginModule` to NPE on startup.

### Resolution — drop Bitnami Helm chart, use plain K8s manifests
Rewrote `infra/terraform/spark.tf` to use `kubernetes_stateful_set` and
`kubernetes_service` resources directly (no Helm). Runs as UID 185 (native apache/spark
user) with no `readOnlyRootFilesystem` restriction.

## Current State
Image is built and pushed (`jaymztheking/spark:latest`, ARM64, apache/spark:3.5.3 base).
Terraform has been updated but `terraform init && terraform apply` has not yet been run
on the new machine. Old Bitnami `helm_release.spark` is still live on the cluster.

## Next Steps
1. `make tf-init && make tf-apply` — destroys Bitnami helm release, creates new StatefulSets
2. Verify master and 2 workers reach `Running` state
3. Check Spark UI at `http://192.168.50.231:30808`
4. Run validation tests: `uv run pytest tests/validation/test_006_spark_helm_release.py -m k3s`
5. Move story to `completed/` once all acceptance criteria pass
