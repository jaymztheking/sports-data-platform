# MLB Transform Airflow DAG

**Phase**: 3 — Silver & Gold Layers
**Story Points**: 2

## User Story
As a data engineer, I want an Airflow DAG that runs dbt models for MLB so that staging and mart layers stay up to date after ingestion.

## Acceptance Criteria
- [x] `mlb_transform_dag.py` runs staging models, then marts, then tests sequentially
- [x] Uses dbt CLI with `--select` tag filters for MLB
- [x] Manually triggered (downstream of ingestion)
- [x] Tagged with `mlb`, `transform`, `dbt`
