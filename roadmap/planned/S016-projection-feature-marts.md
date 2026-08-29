# S016 — Projection feature marts (environment, role, line)

**Phase**: 2 — Our own projections
**Functional unit**: staging → `int_` feature marts the projection model consumes

> First of three stories that replace the borrowed ECR board with our own numbers.
> **S016 features → S017 backtest → S018 projection + rankings.**

## User Story
As a fantasy manager, I want each player's 2026 *environment* and *role* expressed as
features, so that a projection can reason about opportunity rather than just repeating
last season's box score.

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
