# Backlog — Phase 2 (broaden products) & Phase 3 (prod on k3s)

Thin stubs; each becomes its own `SNNN-*.md` with full acceptance criteria when pulled
into `planned/`.

## Phase 2 — Broaden data products (still dev-only DuckDB)
- **S007 — Ingest pbp + rosters + snap counts + injuries.** More `nflreadpy` modules → Parquet
  + samples: `load_pbp`, `load_rosters_weekly`, `load_snap_counts`, `load_injuries`.
  Note `pbp` is ~13 MB/season (49k rows × 372 cols) — it needs a real `data/samples/` slice
  (a couple of games), not a token filter. The other three are <1 MB/season.
- **S008 — Usage/opportunity intermediates.** `int_` models: target share, air-yards share,
  red-zone touches, snap %. **Snap % and red-zone touches were split out of S005** — they
  depend on `snap_counts`/`pbp`, which S007 ingests. Hard dependency: S007 → S008.
- **S009 — Matchup context marts.** `mart_positional_defense` (fantasy points allowed to each position) + `mart_strength_of_schedule`.
- **S010 — Waiver/trend marts.** `mart_waiver_targets` (usage spikes) + `mart_player_trends`.

### Ingest scope — which `nflreadpy` loaders we pull

A loader gets ingested only when a named mart needs it. Interesting ≠ in scope.

- **In:** `load_player_stats`, `load_schedules` (S003) · `load_pbp`, `load_rosters_weekly`,
  `load_snap_counts`, `load_injuries` (S007) · `load_players`, `load_teams` when a dim needs
  them · `load_depth_charts` (S010, role change = the waiver signal).
- **Out:** `load_contracts`, `load_combine`, `load_draft_picks`, `load_trades`,
  `load_officials`, `load_ftn_charting`, `load_pfr_advstats`, `load_nextgen_stats`,
  `load_participation` — no mart consumes them.
- **Deliberately out:** `load_ff_opportunity`, `load_ff_rankings`, `load_ff_playerids`.
  These are nflverse's *precomputed* fantasy analytics (expected points, others' rankings).
  Ingesting them would make our headline products a wrapper around someone else's model
  instead of our dbt — `ff_opportunity`'s 159 columns of expected-points modeling is
  precisely what S008/S010 exist to build.

## Phase 3 — Prod on simplified k3s + serving + schedule
- **S011 — Slim infra.** Terraform/Helm = Postgres only + secrets (trim old `infra/terraform/{postgres,main,versions,variables,ingress}.tf`; drop spark/iceberg/minio/airflow/mlflow).
- **S012 — Prod build path.** k3s job loads `raw_nfl` (Postgres) + `dbt build --target prod`; verify enforced contracts hold on Postgres (cross-adapter gate). k3s integration tests.
- **S013 — Weekly schedule.** k3s CronJob, in-season cadence.
- **S014 — Self-hosted BI.** Evidence.dev (static → nginx) or Metabase at `*.sports.data`. Decide the tool here.
- **S015 — Deploy workflow + docs.** Self-hosted-runner deploy workflow; architecture docs; README polish.


---

## Deferred from S003A (2026-08-28) — deepen the history window

`history_start_season` currently starts at **2022** (4 seasons). That was a time call
before the 2026-09-05 draft, not a judgement about what is useful. nflverse player stats
reach back to **1999**, and the knob is a single env var — no code change needed to widen.

Worth doing once the draft board ships, because more history is what makes the
season-over-season features possible: age curves, true breakout-vs-outlier separation,
regression-to-mean priors, and career-arc context. Check ingest runtime and Parquet size
before going all the way back — 4 seasons is 2.0 MB, so ~25 seasons is likely ~12 MB,
which is fine locally but worth confirming against the k3s Postgres load path (S011+).
