# CLAUDE.md

> **Start every session by reading `HANDOFF.md`** — it holds the current board state and the next action. This file holds the durable rules.

## Project

An **NFL fantasy-football data platform**, built as a portfolio piece. dbt is the center of gravity. It ingests nflverse data with `nflreadpy`, transforms it through a medallion dbt project, and produces marts that help with fantasy decisions (weekly scoring, usage/opportunity, matchups, waiver targets). It runs and refreshes weekly during the season.

See `README.md` for architecture and how-to-run.

## The one rule that matters: cohesion over volume

A previous version of this repo "became a pile of Claude-generated code that was not cohesive." The root cause was **infrastructure weight** — Spark/Iceberg/MinIO/Airflow/MLflow/k3s were all stood up before any dbt value existed, and the code sprawled. We are deliberately inverting that: **ship working data products on light local tooling first; add self-hosted infra last.**

### Collaboration protocol (how we work)
1. **One story = one functional unit = one feature branch = one PR.** Nothing lands on `main` except through a reviewed PR. `main` is branch-protected.
2. **TDD-first.** Write the story's tests / dbt contracts before implementation.
3. **Division of labor (default):** Claude scaffolds the skeleton (file stubs, `sources.yml` / contract YAML, one *reference* model or test). **James hand-writes the core SQL/Python.** Then Claude reviews and they iterate. **Claude does not bulk-generate models/logic across a story** unless James explicitly asks for a full draft. This is the anti-"pile" guardrail — respect it.
4. Keep PRs small and legible. Prefer a working thin slice over a broad half-built layer.

## Architecture (light on purpose)

```
nflreadpy (Polars ingest, hand-coded Python)
  ├─ dev  → Parquet in data/raw/ (committed sample in data/samples/ for CI)
  └─ prod → k3s CronJob loads raw_nfl.* tables in Postgres
        ↓  dbt sources — the same source() refs resolve in each engine
   staging (views) → intermediate (views) → marts (tables, contracts enforced)
        dev  → local nfl.duckdb   (dbt-duckdb)
        prod → k3s PostgreSQL     (dbt-postgres)
        ↓
   Self-hosted BI at *.sports.data
```

**Two environments, not three. CI is a mechanism, not an environment.** There are exactly two dbt targets — `dev` (DuckDB) and `prod` (Postgres). CI is the promotion gate between them: on every PR it runs the **`dev`** target ephemerally (`NFL_DUCKDB_PATH=:memory:`) against the committed sample, and it must pass before code can merge and reach prod. Do not add a `ci` target.

**Cross-adapter is deliberate.** dev uses DuckDB, prod uses Postgres. The friction (contract `data_type` names, a few SQL functions) is isolated: contracts use the portable type subset; CI validates the build on DuckDB, and the prod-deploy story validates the same contracts on Postgres so drift can't reach prod silently.

## Conventions

- Package manager: **uv**. Python 3.11–3.13.
- Python lint/type: **ruff** + **mypy** (strict, third-party ignores in `pyproject.toml`).
- SQL lint: **sqlfluff** (dbt templater).
- Tests: **pytest** for Python; **dbt tests + dbt unit tests + contracts** for models. `@pytest.mark.k3s` marks prod/cluster tests (skipped in CI).
- Ingestion library: **`nflreadpy`** (the older `nfl_data_py` is deprecated — do not use it).
- dbt env differences = connection + schema only, via `profiles.yml` targets + a `generate_schema_name` override keyed on `target.name`.

## Roadmap / story model

Stories live in `roadmap/` swim lanes and each is one **functional unit** (one source→destination hop, or one cohesive deliverable).

```
roadmap/
  backlog/       deferred, not on the near-term radar
  planned/       spec / acceptance criteria only, nothing written
  tests_written  tests written first, implementation not yet complete
  active/        currently being worked (WIP)
  validating/    tests + implementation done; local green, prod/k3s pending
  completed/     done and validated
  blocked/       waiting on a dependency/decision
```

- **Definition of done:** the story's tests pass (local tier always; the k3s tier for prod stories once the cluster runs). A story moves to `completed/` only when its acceptance criteria are met and proven by tests.
- Custom agents: `.claude/agents/scrum-master.md` (reports lane moves — does not move files itself) and `.claude/agents/test-writer.md` (drafts acceptance tests from a story's ACs).
