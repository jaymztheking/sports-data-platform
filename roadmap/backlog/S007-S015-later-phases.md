# Backlog — Phase 2 (broaden products) & Phase 3 (prod on k3s)

Thin stubs; each becomes its own `SNNN-*.md` with full acceptance criteria when pulled
into `planned/`.

## Phase 2 — Broaden data products (still dev-only DuckDB)
- **S007 — promoted to `roadmap/planned/S007-ingest-widening.md` 2026-08-29** (widened the
  same day for the projection stories S016–S018: `pfr_advstats`, `ff_opportunity`,
  `team_stats`, `draft_picks`, `depth_charts`, 2026 `schedules`, plus two new non-nflreadpy
  ADP ingest modules — ESPN and FFC — with dated snapshotting for `ff_rankings`/ESPN ADP).
  Full acceptance criteria live in that file now; this stub is kept only for the
  `load_pbp`/`load_rosters_weekly`/`load_injuries` sample-only additions it still owns for
  S008, and for the "Ingest scope" table below (note: that table's "deliberately out" call
  on `load_ff_opportunity` is superseded — see the promoted S007 file).
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


---

## Phase 2b — Our own projections (planned 2026-08-29)

Promoted out of backlog into `roadmap/planned/` as **S016 → S017 → S018**. Replaces the
borrowed ECR rankings with our own forecast. Sequence matters: features, then the
**backtest harness**, then the model — the scoreboard is built before the thing it scores.

Deferred to a later story: **weekly projections**, built as
`season baseline × weekly modifier` (opponent, spread, game script, injury). The
dependency runs season → weekly deliberately, so that Week 1 matchups cannot leak into a
draft ranking.


---

## Dropped 2026-09-06 — ESPN league sync (was S019)

Cut before it was written. The valuable half (league scoring and roster settings) was
done **manually** — both rulebooks pasted in and encoded as the `kiddy` and `ppr` formats,
plus `league_settings.csv` for lineup shape. Rules change once a year in July, so an API
to fetch them earns very little. The other half, live auto cross-off, could not be vetted
before the drafts, and `S005C`'s manual cross-off already covers it and cannot break.

Keeping only what the probing established, so it does not have to be re-derived:

- **ESPN's API is one URL per league with `?view=` selecting the slice** —
  `.../seasons/2026/segments/0/leagues/{id}?view=mSettings|mDraftDetail|mRoster|mTeam`.
- **Auth is unresolvable without a real league id.** The endpoint returns
  **401 `AUTH_LEAGUE_NOT_VISIBLE`** for *private and nonexistent leagues alike*, so probing
  cannot tell which case applies. Public leagues need no auth; private ones need `espn_s2`
  and `SWID` cookies, which expire and are credentials.
- **Mock draft lobbies are not REST-addressable.** The lobby page loads but is a JS app
  exposing no endpoints, and there is no mock segment (`segments/1` → 404). Live drafts are
  most likely websocket-driven by the draft client. A **throwaway ESPN league** is the
  reliable disposable target instead — free, real league id, identical REST surface, and
  public if you set it so.
- **The open question, if this ever returns:** does `mDraftDetail` update *during* a live
  draft, or only settle once it ends? Auto cross-off is impossible over REST if the latter,
  and it cannot be tested during a real draft.
- **Privacy:** rosters and draft picks carry other managers' names. They belong in no
  committed sample and no published artifact.
