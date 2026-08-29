# S016 — Projection feature marts (environment, role, line)

**Phase**: 2 — Our own projections
**Functional unit**: staging → `int_` feature marts the projection model consumes

> First of three stories that replace the borrowed ECR board with our own numbers.
> **S016 features → S017 backtest → S018 projection + rankings.**

## User Story
As a fantasy manager, I want each player's 2026 *environment* and *role* expressed as
features, so that we can explain **where expert consensus (ECR) departs from where the
crowd actually drafts (ADP)** — and tell which of those departures are real.

## The goal is not to beat ECR
Earlier framing ("out-predict consensus") was wrong and is dropped. ECR already
aggregates camp reports, scheme changes and injury nuance we cannot see. **ADP is the
exploitable side**: it is revealed crowd behaviour — name recognition, recency, hype —
and it lags the information ECR already contains.

The job is to **amplify ECR's signal over ADP**: build the structural features that ECR
is implicitly weighing, so a divergence can be corroborated rather than taken on faith.

## Context: what the current board is and isn't
`fct_player_season` (S005A) contains **no projections**. The rankings in it are
FantasyPros ECR passed through unchanged; the production side is our arithmetic on
nflverse box scores. `value_over_ecr` is "last season's results vs. this season's
consensus" — not a model output. This story begins the actual modelling.

## Scope
Feature marts only. No projection, no model, no rankings — those are S017/S018.

### Verified available (probed 2026-08-29, all free, all in `nflreadpy`)
| Feature group | Source | Note |
|---|---|---|
| Vegas | `load_schedules(2026)` | 112 of 272 games priced; **all 32 teams covered**, median 7 games each |
| Run blocking | `pfr_advstats(stat_type='rush')` | `ybc_att` — yards before contact per attempt |
| Pass protection | `pfr_advstats(stat_type='pass')` | `pressure_pct`, `times_blitzed`, `pocket_time` |
| Team pace / defense | `load_team_stats` | 136 cols, incl. EPA, per team-season |
| Playing time | `load_snap_counts` | `offense_pct` — the real "sees the field" measure |
| 2026 role | `load_depth_charts(2026)` | `pos_rank`, `pos_slot`; covers rookies |
| Luck-stripped production | `load_ff_opportunity` | `*_exp` expected columns |
| Rookie draft capital | `load_draft_picks` | closes the 15 blank rookies on the board |
| **ADP — live market** | **ESPN fantasy API** | free, no auth. `ownership.averageDraftPosition`. **This is the market James drafts in** |
| **ADP — history** | **Fantasy Football Calculator API** | free, no key, no tier. 2026: 8,162 drafts. Verified history 2022/2024/2025 |

### Two ADP sources, and they are not interchangeable
**James drafts on ESPN**, so ESPN ADP is the market to model. Measured 2026-08-29 against
FFC on 233 shared players: mean absolute difference **13.8 picks**, median 10.8, max 55.6
— **107 of 233 differ by more than a full round**. Sam LaPorta is ESPN 72 / FFC 118;
Chris Godwin ESPN 135 / FFC 80. Optimising against FFC while drafting on ESPN would be
optimising against the wrong crowd.

But **ESPN history is unreliable**: 2024 returns real ADP while 2025 returns a constant
`170.0` sentinel for every player. FFC history is clean. So:

- **ESPN → live decisions.** The market we are actually beating.
- **FFC → backtesting.** The only trustworthy multi-season ADP.

Validate any ESPN historical pull before trusting it — a column of identical values is
the failure mode, and it will not error.

There is a sharper edge here than generic crowd bias: ESPN draft rooms display ESPN's own
rankings, so ESPN ADP is anchored to ESPN editorial ranks. The ECR-vs-ESPN-ADP gap is
therefore substantially *FantasyPros consensus vs. ESPN's in-house ranking* — a
systematic, repeatable difference rather than random noise.

Neither source is in `nflreadpy`; both are plain public JSON APIs with no key and no tier,
so both clear the cost rule. Each needs its own ingest module.

### ⚠️ Snapshot ECR and ESPN ADP now — they have no history
`ff_rankings` and ESPN ADP are **live snapshots**. Today's board is gone tomorrow, and
without a stored history there is nothing to backtest ECR against, ever. Start writing a
dated snapshot on every ingest run **before** S016 begins; it is a few lines and the cost
of skipping it is a year of lost data.

**Hard dependency:** S007 must widen its ingest scope to cover
`pfr_advstats`, `ff_opportunity`, `team_stats`, `draft_picks`, `depth_charts`,
and the **2026** schedule. S007 → S016.

## Acceptance Criteria

### Implementation
- [ ] `int_team_environment` — per team-season:
      - **`implied_team_total`** = `total_line/2 - spread_line/2`, averaged over that
        team's priced games. The strongest single Vegas signal for fantasy.
      - **`avg_spread`** — game-script lean (favoured teams run more).
      - plays per game / pace, from `team_stats`.
- [ ] `int_team_line_quality` — `ybc_att` (run block) and `pressure_pct` (pass pro),
      as multi-season averages so one bad year does not swing it.
- [ ] `int_player_role` — `offense_pct` history + 2026 `pos_rank`/`pos_slot`, plus
      rookie draft capital. Role is what makes a rookie projectable at all.
- [ ] `int_player_efficiency_priors` — per-player rate stats **regressed toward the
      positional mean**, with the shrinkage weight a documented `var`.
- [ ] `_nfl__intermediate.yml` — tests on every grain; no silent fan-out.

### Validation
- [ ] `dbt build` green on sample and full history
- [ ] every feature has a **non-null rate check** and a documented range
- [ ] no feature computed from the season being predicted (leakage check — see S017)

## The positional-scale correction (measured 2026-08-29 — encode it, do not re-derive it)
**The raw `ADP − ECR` gap is dominated by position, not by player.** Measured on the live
2026 board joined to 8,162 drafts:

| Position | mean raw gap |
|---|---|
| QB | **+11.6** |
| TE | +10.1 |
| RB | −7.5 |
| WR | **−10.3** |

A 22-spot structural swing from QB to WR carrying **zero player information**. Experts
rank quarterbacks on raw value; drafters wait on QB because only one starts and
replacement level is shallow. Sorted on the raw gap, the top 12 "values" were 8 QBs and
3 TEs and the bottom was entirely WRs — the ranking was reporting roster construction.

**Every ECR/ADP comparison must be computed on within-position ranks.** Done that way the
gaps collapse to a realistic ±11 and become player-level disagreement. This is the same
class of defect as the population mismatch caught in S005A.

## Two independent uncertainty signals — use both
`ecr_stddev` is *expert* disagreement; FFC's `stdev` is *crowd* disagreement. They are
measured on different populations and are not interchangeable. A player both sides agree
on is a different proposition from one where only the crowd is split, and the second is
where a structural feature has something to add.

## The game-script correction (encode this, do not re-derive it)
The intuition "players on good-defence teams see the field more" **is not the mechanism**
and, modelled naively, cancels to noise. Snap share is set by depth-chart role, not team
quality — a WR1 on a bad team still plays ~90% of snaps. The real mechanism is game
script, and it has **opposite signs by position**:

- good defence → team leads → clock-killing runs → **RB carries up, pass volume down**
- bad defence → team trails → catch-up passing → **WR/TE targets up, RB carries down**

So team strength must enter the model **interacted with position**, never as a single
"good team is good" term. `implied_team_total` and `avg_spread` encode this cleanly.

## Definition of Done
Feature marts build green, are tested for grain and range, and are documented well enough
that S018 can consume them without re-reading this story.
