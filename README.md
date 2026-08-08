# NFL Fantasy Football Data Platform

A portfolio data platform for fantasy football, centered on **dbt**. It ingests
[nflverse](https://github.com/nflverse) data with `nflreadpy`, models it through a
medallion dbt project, and produces marts that help with real fantasy decisions —
weekly scoring, usage/opportunity, matchups, and waiver targets — refreshed weekly
during the season.

It is intentionally **light**: the value (dbt models + data contracts) comes first,
and self-hosted infrastructure is added only at the end.

## Highlights (what this repo demonstrates)

- **dbt at the center** — medallion layering (staging → intermediate → marts) with
  enforced **data contracts**, source freshness, generic + `dbt_expectations` tests,
  and **dbt unit tests** on hand-coded fantasy-scoring logic.
- **Real dev/prod environment separation in dbt** — two targets that differ only by
  connection + schema (`generate_schema_name` keyed on `target.name`).
- **CI as the promotion gate** — CI isn't a third environment; every PR runs lint,
  type-check, tests, sqlfluff, and a full `dbt build` of the **`dev`** target ephemerally
  (`NFL_DUCKDB_PATH=:memory:`) against committed sample data. It must pass before code
  reaches prod.
- **Cross-adapter portability** — the same models run on DuckDB (dev) and Postgres (prod).

## Architecture

```
nflreadpy (Polars ingest)
  ├─ dev  → Parquet in data/raw/   (committed sample in data/samples/ for CI)
  └─ prod → k3s CronJob loads raw_nfl.* in Postgres
        ↓  dbt sources (same source() refs resolve in each engine)
   staging (views) → intermediate (views) → marts (tables, contracts enforced)
        dev  → local nfl.duckdb   (dbt-duckdb)
        prod → k3s PostgreSQL     (dbt-postgres)
        ↓
   Self-hosted BI at *.sports.data
```

Two environments — `dev` and `prod`:

| Environment | Engine | dbt adapter | Data source | Schema |
|-------------|--------|-------------|-------------|--------|
| `dev`  | local DuckDB file | `dbt-duckdb`  | `data/raw/*.parquet` | `dev` |
| `prod` | k3s PostgreSQL    | `dbt-postgres`| `raw_nfl.*` tables   | `staging` / `marts` |

**CI** is not an environment — it is the dev→prod gate. On every PR it runs the `dev`
target ephemerally (`NFL_DUCKDB_PATH=:memory:`) against `data/samples/*.parquet`, and it
must pass before code can merge and reach prod.

## Getting started (local dev)

> Requires [uv](https://docs.astral.sh/uv/). Populated end-to-end from `S003` onward.

```bash
uv sync --extra dbt --extra dev          # install deps
# (S003+) pull data → data/raw/*.parquet:
uv run python -m nfl.ingest.player_stats --season 2025
uv run python -m nfl.ingest.schedules --season 2025
cd dbt_project
uv run dbt deps
uv run dbt build --target dev            # build nfl.duckdb, run tests + contracts
```

## Status

Early build. See `HANDOFF.md` for the current board state and `roadmap/` for the
story backlog. `CLAUDE.md` documents the durable rules and collaboration protocol.
