# Run MLB Ingestion End-to-End

**Phase**: 2 — Bronze Layer
**Story Points**: 5

## User Story
As a data engineer, I want to trigger the MLB ingestion DAG and see data flow from pybaseball through Spark into Iceberg and Postgres so that the bronze layer is validated.

## Acceptance Criteria
- [ ] MLB ingestion DAG visible and triggerable in Airflow UI
- [ ] Statcast, batting, pitching, and schedule tasks complete successfully
- [ ] Iceberg tables exist in MinIO under `spark-warehouse/`
- [ ] `spark-sql` can query Iceberg tables and return results
- [ ] `raw_mlb` schema in PostgreSQL contains statcast, batting, pitching, schedules tables
- [ ] Data row counts are reasonable for the ingested season
