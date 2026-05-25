# HANDOFF

Read this at the start of every session, then `CLAUDE.md`.

## Where we are (last updated 2026-05-24)

We tore down the old fragmented roadmap and rebuilt it as **functional-unit stories** (one source→destination hop each), then wrote story 011's tests TDD-first.

### Roadmap state (`roadmap/<lane>/`)
- **completed/**: infra 001–007, plus 043 (CI fix), 044 (secret rotation)
- **validating/**: 008 (mlflow), 009 (custom images), **011** (MLB pybaseball→Iceberg — tests written, impl present, local tier green, k3s NOT yet run)
- **planned/**: 012 (Iceberg→Postgres), 013 (raw→dbt marts), 014 (gold→MLflow), 025 (cross-sport schedule), 038–042 (polish: sqlfluff/docs/setup/readme/CI)
- **backlog/**: 010 (GitHub Actions), 015–024 (NFL/NBA/NHL verticals)
- **tests_written/**, **active/**, **blocked/**: empty

### Lifecycle (lanes = next action)
`planned` (spec only) → `tests_written` (tests done, impl pending) → `validating` (tests+impl done, local green, k3s pending) → `completed` (k3s passed). `backlog`=deferred, `blocked`=waiting, `active`=WIP.

### Hard rules (also in CLAUDE.md)
- One story = one functional unit, confirmed by its own tests. Never a tests-only or impl-only story.
- **TDD: write ALL tests first** (unit/structural + k3s integration + data-contract), then implement to green.
- The **story** is the unit of cohesion, not the test file — tests may span `tests/unit|integration|validation/`.
- **Only code backing a validating/completed/active story exists in the repo.** Impl for planned/backlog stories was cleared; it comes back tests-first when the story is worked.
- Definition of done: local tier green AND k3s integration passes on the live cluster.

## Story 011 — current detail
- Tests: `tests/validation/test_011_mlb_ingest_to_iceberg.py`
  - **Tier 1 (38 tests, local, no marker)**: config/storage real-import; spark/ingestion/DAG via AST (metadata contract, partition scheme, `writeTo` target, 30-team source of truth, DAG decorator/parallelism). Plus `tests/unit/test_config.py` (belongs to 011).
  - **Tier 2 (15 tests, `@pytest.mark.k3s`)**: module fixture execs an in-Airflow-pod driver that micro-ingests all four tables into a throwaway `iceberg.mlb_ci` namespace (1-day statcast, 1-season batting/pitching, 2-team schedules), captures row counts, tears down. Asserts namespace/tables via Iceberg REST, metadata cols in each schema, `season=` partitions + data files in MinIO, positive row counts, DAG registered/import-error-free.
- Impl kept for 011: `src/common/{config,spark,storage}.py`, `src/domains/mlb/ingestion/*`, `dags/mlb/mlb_ingestion_dag.py`.
- TDD changes the tests forced: added `table=` param to the four `ingest_*` fns (default unchanged) so tests target a throwaway namespace; DAG now imports `schedules.MLB_TEAMS` (was a duplicated literal); removed `load_to_postgres` task from the ingestion DAG (it's 012's).
- Status: local green, ruff clean. **Next: run Tier 2 against the live cluster** (needs `kubectl` + cluster up). Pass → 011 to `completed/`; fail → fix impl, stays in `validating/`.

## Uncommitted
All of the above is **unstaged** (roadmap renames/moves, deleted dead impl, new test file, CLAUDE.md edits). Not yet committed. `roadmap/drafted/` → renamed to `tests_written/`; many old story md's deleted; new functional-unit md's added.

## Next actions (in order)
1. (Optional) Commit the teardown + 011 tests.
2. Run `pytest tests/validation/test_011_mlb_ingest_to_iceberg.py -m k3s` against the cluster; resolve failures.
3. Move 011 to `completed/` when k3s passes.
4. Start story 012 (Iceberg→Postgres) tests-first — no impl exists yet.
