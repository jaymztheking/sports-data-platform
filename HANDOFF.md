# HANDOFF

Read this at the start of every session, then `CLAUDE.md`.

## Where we are (last updated 2026-05-27)

### Roadmap state (`roadmap/<lane>/`)
- **completed/**: infra 001–007, 008 (MLflow deployment), 009 (custom Docker images), 011 (MLB pybaseball→Iceberg), 012 (MLB Iceberg→Postgres), 043 (CI fix), 044 (secret rotation)
- **tests_written/**: empty
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

## Story 012 — COMPLETED ✓
All 17 k3s tests passed (2026-05-27). Schema, tables, row counts, metadata columns, and idempotency all verified.

Key design notes:
- Reads Iceberg via Spark, writes to Postgres via pandas `.to_sql()` + SQLAlchemy (no Spark JDBC)
- `psycopg2-binary` + `sqlalchemy>=2.0` in the ingestion-spark Docker image
- k3s tests use synthetic seed data in isolated namespace `mlb_ci_012` / schema `raw_mlb_ci_012`
- Fixture runs seed + initial load + reload (3 pods total); idempotency tests just query Postgres
- Pod timeout 900s (pods take 5-20 min on ARM64 Raspberry Pi cluster)

## Story 045 — backlog
Baseball Savant Statcast leaderboard API + MLB Stats API to replace bref dependency long-term.
See `roadmap/backlog/045-mlb-stats-api-source.md` for endpoints and acceptance criteria.

## Next actions (in order)
1. Start story 013 (MLB raw→dbt marts) tests-first — spec is in `roadmap/planned/`.
2. Write ALL tests for 013 (unit/structural + k3s integration) before any implementation.
3. After 013 is green: story 014 (gold→MLflow), then 025 (cross-sport schedule), then polish (038–042).

## Production DAG note
`dags/mlb/mlb_ingestion_dag.py` still hardcodes `MINIO_ACCESS_KEY: "minioadmin"` — this is wrong for production. The correct credentials must be injected from K8s secret at DAG runtime (not hardcoded). Fix before any production run.
