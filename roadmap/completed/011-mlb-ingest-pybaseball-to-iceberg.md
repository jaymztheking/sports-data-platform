# MLB Bronze: pybaseball → Iceberg

**Phase**: 2 — Bronze Layer
**Functional unit**: pybaseball → Iceberg tables in MinIO

## User Story
As a data engineer, I want MLB data pulled from pybaseball and written to Iceberg tables in MinIO so that the bronze layer holds raw, queryable MLB data with consistent metadata and partitioning.

## Scope
One source-to-destination hop. Owns everything needed to make that hop run on the cluster: the shared client modules it depends on (config, Spark session factory, MinIO/S3 client), the four ingestion modules, and the Airflow tasks that execute them. The shared clients live here because this is the first pipeline that proves them against real infrastructure.

## Acceptance Criteria

### Implementation
- [x] Shared `config.py` (Pydantic settings with `POSTGRES_`/`MINIO_`/`SPARK_` prefixes), `spark.py` (Iceberg REST-catalog + MinIO SparkSession), `storage.py` (boto3 S3 client)
- [x] `statcast.py`, `batting.py`, `pitching.py`, `schedules.py` fetch from pybaseball and write to `iceberg.mlb.*`
- [x] `schedules.py` covers all 30 MLB teams
- [x] Airflow DAG runs the four ingestions in parallel, each managing its own SparkSession

### Validation — unit / structural (no cluster)
- [x] config env prefixes, SparkSession Iceberg/REST/S3A config keys, client factory signatures
- [x] each ingestion module: function signature, `withColumn` metadata contract (`ingested_at`, `source`, `season`), correct `writeTo("iceberg.mlb.<table>")` target, `partitionedBy("season")`
- [x] `MLB_TEAMS` constant has 30 unique entries

### Validation — k3s integration / data contract (live cluster)
- [x] After a run, Iceberg REST catalog exposes namespace `mlb` with tables `statcast`, `batting`, `pitching`, `schedules`
- [x] Each table schema contains `ingested_at`, `source`, `season`
- [x] Each table is partitioned by season in MinIO (`season=YYYY` prefixes under `spark-warehouse/`)
- [x] Row counts > 0 and plausible for the ingested season
- [x] `spark-sql` can query each table and return rows

## Definition of Done
All unit tests pass locally **and** the k3s integration class passes against the live cluster. Then the story moves to `validating/` → `completed/`.
