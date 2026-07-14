# Backlog — Phase 2 (broaden products) & Phase 3 (prod on k3s)

Thin stubs; each becomes its own `SNNN-*.md` with full acceptance criteria when pulled
into `planned/`.

## Phase 2 — Broaden data products (still dev-only DuckDB)
- **S007 — Ingest pbp + rosters + snap counts + injuries.** More `nflreadpy` modules → Parquet + samples.
- **S008 — Usage/opportunity intermediates.** `int_` models: target share, air-yards share, red-zone touches, snap %.
- **S009 — Matchup context marts.** `mart_positional_defense` (fantasy points allowed to each position) + `mart_strength_of_schedule`.
- **S010 — Waiver/trend marts.** `mart_waiver_targets` (usage spikes) + `mart_player_trends`.

## Phase 3 — Prod on simplified k3s + serving + schedule
- **S011 — Slim infra.** Terraform/Helm = Postgres only + secrets (trim old `infra/terraform/{postgres,main,versions,variables,ingress}.tf`; drop spark/iceberg/minio/airflow/mlflow).
- **S012 — Prod build path.** k3s job loads `raw_nfl` (Postgres) + `dbt build --target prod`; verify enforced contracts hold on Postgres (cross-adapter gate). k3s integration tests.
- **S013 — Weekly schedule.** k3s CronJob, in-season cadence.
- **S014 — Self-hosted BI.** Evidence.dev (static → nginx) or Metabase at `*.sports.data`. Decide the tool here.
- **S015 — Deploy workflow + docs.** Self-hosted-runner deploy workflow; architecture docs; README polish.
