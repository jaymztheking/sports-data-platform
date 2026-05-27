# HANDOFF

Read this at the start of every session, then `CLAUDE.md`.

## Where we are (last updated 2026-05-27)

### Roadmap state (`roadmap/<lane>/`)
- **completed/**: infra 001–007, 008 (MLflow deployment), 009 (custom Docker images), 011 (MLB pybaseball→Iceberg), 043 (CI fix), 044 (secret rotation)
- **tests_written/**: 012 (MLB Iceberg→Postgres — tests written, impl present, k3s pending)
- **planned/**: 013 (raw→dbt marts), 014 (gold→MLflow), 025 (cross-sport schedule), 038–042 (polish)
- **backlog/**: 010 (GitHub Actions), 015–024 (NFL/NBA/NHL verticals), 045 (MLB Baseball Savant Statcast API)
- **active/**, **validating/**, **blocked/**: empty

### Lifecycle (lanes = next action)
`planned` (spec only) → `tests_written` (tests done, impl pending) → `validating` (tests+impl done, local green, k3s pending) → `completed` (k3s passed). `backlog`=deferred, `blocked`=waiting, `active`=WIP.

### Hard rules (also in CLAUDE.md)
- One story = one functional unit, confirmed by its own tests. Never a tests-only or impl-only story.
- **TDD: write ALL tests first** (unit/structural + k3s integration + data-contract), then implement to green.
- The **story** is the unit of cohesion, not the test file — tests may span `tests/unit|integration|validation/`.
- **Only code backing a validating/completed/active story exists in the repo.** Impl for planned/backlog stories was cleared; it comes back tests-first when the story is worked.
- Definition of done: local tier green AND k3s integration passes on the live cluster.
- **NEVER hardcode passwords in Python** — always fetch credentials from K8s secrets at runtime.

## Story 011 — COMPLETED ✓
All 15 k3s integration tests passed (2026-05-27). All four Iceberg tables (statcast, batting, pitching, schedules) confirmed with metadata columns, season partitions, and positive row counts.

Key fixes required to get 011 green:
- Switched batting/pitching from `batting_stats()` / `pitching_stats()` (Fangraphs, CAPTCHA-blocked since April 2026) to `batting_stats_bref()` / `pitching_stats_bref()` (Baseball Reference)
- MinIO credentials fetched from K8s secret `minio` (keys: `rootUser`/`rootPassword`) at runtime — NOT hardcoded
- Added `AWS_REGION=us-east-1`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` for Iceberg S3FileIO (AWS SDK v2)
- Added `CATALOG_S3_PATH__STYLE__ACCESS=true` to iceberg-rest deployment (fixes virtual-hosted URL errors)
- Updated tests to use `local[*]` Spark mode (avoids client-mode reverse-connectivity issues in k3s)

## Story 012 — tests_written (k3s pending)
- Tests: `tests/validation/test_012_mlb_load_to_postgres.py`
- Impl: `src/domains/mlb/load/iceberg_to_postgres.py`, updated DAG `dags/mlb/mlb_ingestion_dag.py`
- Docker: `psycopg2-binary` + `sqlalchemy>=2.0` added to `docker/ingestion-spark/Dockerfile`
- k3s tests use synthetic seed data (no Fangraphs dep), isolated namespace `mlb_ci_012` / schema `raw_mlb_ci_012`
- Postgres password fetched from K8s secret `postgresql` key `postgres-password` at runtime
- **Next: run k3s tests** → if pass, move to `validating/` (then `completed/` when k3s confirmed)

## Story 045 — backlog
Baseball Savant Statcast leaderboard API + MLB Stats API to replace bref dependency long-term.
See `roadmap/backlog/045-mlb-stats-api-source.md` for endpoints and acceptance criteria.

## Next actions (in order)
1. Run `pytest tests/validation/test_012_mlb_load_to_postgres.py -m k3s -v --tb=short` against the cluster.
2. If pass → move 012 to `validating/` (impl already present), commit, then run again to confirm → `completed/`.
3. Start story 013 (Iceberg→dbt marts) tests-first.

## Production DAG note
`dags/mlb/mlb_ingestion_dag.py` still hardcodes `MINIO_ACCESS_KEY: "minioadmin"` — this is wrong for production. The correct credentials must be injected from K8s secret at DAG runtime (not hardcoded). Fix before any production run.
