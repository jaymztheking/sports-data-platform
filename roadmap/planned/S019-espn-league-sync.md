# S019 — ESPN league sync

**Phase**: 2 — league-aware products
**Functional unit**: ESPN fantasy API → `raw_espn.*` → league-scoped marts

> The board currently answers "who is good?" This story makes it answer
> **"who is good *in James's league*, and who is left?"**

## User Story
As someone in two ESPN leagues, I want the platform to know my league's rules, my roster,
and who has already been taken, so that its output is about my team rather than about
fantasy football in general.

## What the "views" are
ESPN's fantasy API is one URL per league:

```
https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leagues/{LEAGUE_ID}
```

You do not ask for different *endpoints* — you ask the same URL for different **views**,
via `?view=`. The view decides which slice of the league comes back. Demonstrated on the
public season endpoint: no view returns `abbrev, active, currentScoringPeriod, gameId…`;
`?view=proTeamSchedules_wl` on the identical URL returns `display, settings`. Same address,
different payload.

The views this story needs, in plain terms:

| View | Plain English |
|---|---|
| `mSettings` | **The league's rulebook.** How many points a receiving yard is worth, how many teams, which roster slots start, PPR or not. |
| `mDraftDetail` | **The draft log.** Every pick: which team took which player at which slot. |
| `mRoster` | **Who currently owns whom**, week by week — including James's own team. |
| `mTeam` | Team names, records, owners. Mostly needed to label the above. |

## Staging: build against a throwaway league first
James's call, and it is the right one. **Do not point the first version at a real league.**

A disposable target removes three risks at once: no credentials to handle while the ingest
is still wrong, no other people's names in play, and a draft you can re-run on demand
instead of once a year.

Two ways to get one, and they are not equally reliable:

- **A throwaway ESPN league — recommended, and verified to work.** Creating a league is
  free and gives a **real league id on the identical REST API**. Set it public and there is
  no auth at all; run a solo autodraft and `mDraftDetail` fills with real pick data. Fully
  controllable, repeatable, no one else's data.
- **ESPN's mock draft lobby — attractive but unconfirmed.** The lobby page loads (HTTP 200)
  but is a JavaScript app; probing it surfaced no REST endpoints, and the v3 API has no
  "mock" segment (`segments/1` → 404). Live mock drafts are most likely driven over
  websockets by the draft client rather than the REST API this story uses. **Treat mock
  lobbies as unproven** — if they turn out to be reachable, good, but do not make the story
  depend on it.

So: throwaway league → verify every view and the whole dbt path → only then point at the
real leagues, and only then deal with cookies if they are private.

## The highest-value piece is not the draft sync
Ranked by value per unit of effort, and this order is deliberate:

### 1. `mSettings` — the league's *actual* scoring and roster rules ⭐
`seeds/scoring_rules.csv` is generic PPR. Real ESPN leagues differ: TE premium, 6-point
passing TDs, decimal scoring, bonus tiers. **Every number on the board is currently scored
to a league James is not in.**

`mSettings` also carries roster slots and team count, which set positional scarcity —
a 12-team 1-QB league and a 10-team superflex value the same player completely differently.
This is a small ingest and it re-prices the entire product. Do it first.

### 2. `mDraftDetail` — picks
Post-draft this gives the full pick list: who went where, and what each team holds. It is
also what would drive auto cross-off (below).

### 3. `mRoster` — weekly rosters
The in-season payoff. Once the platform knows James's roster it can do start/sit,
bye-week conflicts, and waiver targets that fill *his* holes rather than listing the best
available player generally. This is what makes the platform useful for 18 weeks instead
of one afternoon.

### 4. Live draft auto-cross-off — *last, and optional*
Polling `mDraftDetail` during a draft to strike players off automatically. Deliberately
ranked last: it is the flashiest piece and the least valuable. It replaces a single click
per pick, works ~3 hours per year, and needs a polling loop with failure handling on the
one day of the year where a bug is most expensive. `S005C`'s manual cross-off already
covers the need, and it cannot break.

## Auth — the open question
Probed 2026-09-06: `lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2026/segments/0/leagues/{id}`
returns **401 `AUTH_LEAGUE_NOT_VISIBLE`** for an unknown id. ESPN answers identically for
*private* and *nonexistent* leagues, so the probe cannot tell us which case applies without
a real league id.

- **If the leagues are public** — no auth needed, plain GETs, nothing to store.
- **If private** — needs `espn_s2` and `SWID` cookies from a logged-in browser session.
  Those are **credentials**: `.env` locally (gitignored), k3s secrets in prod, never in the
  repo, never in a committed sample. They also expire, so ingest must fail loudly with a
  "cookies expired" message rather than silently returning empty rosters.

**Blocked on:** James's league id(s) and whether each league is public or private.

## Acceptance Criteria

### Implementation
- [ ] **Stage 1 — throwaway league.** Every view proven end-to-end against a disposable
      public league before any real league id is configured, and before any credential
      handling exists
- [ ] `src/nfl/ingest/espn_league.py` — one module, views as sub-commands
      (`--view settings|draft|roster`), league id + season from config
- [ ] `NFL_ESPN_LEAGUE_IDS` in `config.py`; cookies from env only, never arguments
- [ ] `seeds/scoring_rules.csv` **derived from `mSettings`** rather than hand-written,
      with the generic PPR rows kept as a fallback for when no league is configured
- [ ] `stg_espn__league_settings`, `stg_espn__draft_picks`, `stg_espn__rosters`
- [ ] `int_league_scoring` — replaces the generic seed in `int_player_week_points`
- [ ] committed sample must be **fully anonymised** — synthetic league id, no real team or
      manager names. Real league data is personal to other people in the league.

### Validation
- [ ] unit tests mock the HTTP layer; no network in CI (same pattern as the nflverse ingest)
- [ ] expired/invalid cookies produce a clear error, not an empty frame
- [ ] a league with non-PPR settings changes mart output — proven by a test, since
      "scoring is now league-accurate" is otherwise unfalsifiable
- [ ] `dbt build` green on sample and full history

## Definition of Done
The board is scored to James's actual league rules, and the platform knows his roster.

## Note on the other people in the league
Rosters and draft picks contain other managers' names and teams. Keep it out of committed
samples, out of artifacts, and out of anything published. The board is shareable; a league
dump is not.
