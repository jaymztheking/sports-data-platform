# Common Python Modules

**Phase**: 2 — Bronze Layer
**Story Points**: 3

## User Story
As a developer, I want shared configuration and client factories so that all domains use consistent connections to Spark, PostgreSQL, and MinIO.

## Acceptance Criteria
- [x] `config.py` uses Pydantic Settings with env var prefixes for Postgres, MinIO, and Spark
- [x] `spark.py` creates Iceberg-configured SparkSession pointing to REST catalog + MinIO
- [x] `postgres.py` creates SQLAlchemy engine from config
- [x] `storage.py` creates boto3 S3 client configured for MinIO
- [x] All modules import cleanly
