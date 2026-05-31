# Cluster Services

All services run on the K3s cluster at `192.168.50.231`. DNS names require Pi-hole to be configured (see setup below). NodePort URLs work from any machine that can reach the cluster IP directly.

## Browser UIs

| Service | DNS URL | NodePort fallback | Notes |
|---------|---------|-------------------|-------|
| Portal | http://sports.data | — | Links to all services below |
| Airflow | http://airflow.sports.data | http://192.168.50.231:30007 | DAG authoring and run history |
| MinIO Console | http://minio.sports.data | http://192.168.50.231:30090 | Browse/manage S3 buckets |
| Spark Master UI | http://spark.sports.data | http://192.168.50.231:30808 | Active jobs, workers, executors |
| MLflow | http://mlflow.sports.data | http://192.168.50.231:30500 | Experiment tracking, model registry |

## API / Database Endpoints

| Service | Endpoint | Notes |
|---------|----------|-------|
| MinIO S3 API | http://192.168.50.231:30900 | S3-compatible object storage |
| Iceberg REST Catalog | http://iceberg.sports.data (or http://192.168.50.231:30181) | `/v1/namespaces`, `/v1/namespaces/{ns}/tables` |
| PostgreSQL | 192.168.50.231:30432 | databases: `sports_data`, `airflow`, `mlflow` |

## Credentials

- **MinIO**: root credentials in k8s secret `minio` (`rootUser` / `rootPassword`), namespace `data-platform`
- **PostgreSQL**: password in k8s secret `postgresql` (`postgres-password`), namespace `data-platform`

## Pi-hole DNS Setup

To use the `*.sports.data` DNS names, add the following records in Pi-hole:  
**Settings → Local DNS → DNS Records**

| Domain | IP |
|--------|----|
| `sports.data` | `192.168.50.231` |
| `airflow.sports.data` | `192.168.50.231` |
| `minio.sports.data` | `192.168.50.231` |
| `spark.sports.data` | `192.168.50.231` |
| `mlflow.sports.data` | `192.168.50.231` |
| `iceberg.sports.data` | `192.168.50.231` |
