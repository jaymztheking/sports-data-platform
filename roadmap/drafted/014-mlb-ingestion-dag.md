# MLB Ingestion Airflow DAG

**Phase**: 2 — Bronze Layer
**Story Points**: 3

## User Story
As a data engineer, I want an Airflow DAG that orchestrates MLB data ingestion so that the bronze layer is refreshed on a schedule.

## Acceptance Criteria
- [x] `mlb_ingestion_dag.py` uses `@dag` / `@task` decorators
- [x] Statcast, batting, pitching, and schedule tasks run in parallel
- [x] `load_to_postgres` task runs after all ingestion tasks complete
- [x] Each task creates and properly closes its own SparkSession
- [x] DAG scheduled weekly with `catchup=False`
- [x] Tagged with `mlb`, `ingestion`, `bronze`
