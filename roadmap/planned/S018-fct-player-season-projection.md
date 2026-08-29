# S018 — `fct_player_season_projection` + our own rankings

**Phase**: 2 — Our own projections
**Functional unit**: feature marts → projected 2026 season → our rankings

> The payoff story: the first numbers in this repo that are **ours**.
>
> **Not** "our projection vs. ECR". The output is **ECR signal amplified over ESPN ADP**,
> corroborated by structural features — where the crowd is drafting against what
> consensus already knows, and which of those gaps our features support.

## User Story
As a fantasy manager, I want a projected 2026 season for every player and a ranking
built from it, so that I draft on our own forecast rather than on a description of last
season plus somebody else's opinion.

## Scope
Structural projection in **dbt SQL**. No Python model layer, no training loop, no model
artifacts — that lifecycle is the infrastructure weight that sank the previous repo, and
a well-built structural projection is competitive with ML for fantasy. An ML layer is
revisited only if S017's backtest shows the rules leaving something on the table.

## The season projection is matchup-NEUTRAL
**Do not build this by summing weekly projections.** Week 1's opponent must not move a
draft ranking — a player who happens to open against a weak secondary is not a better
draft pick for it. The season model projects a player's *baseline* from role, volume
share, efficiency priors, and season-level environment.

The dependency therefore runs **season → weekly**, not the reverse. A later weekly story
becomes `season baseline per-game rate × weekly modifier` (opponent, spread, game script,
injury), which keeps matchup effects where they belong.

## Model structure
```
projected_points = Σ (projected_volume × projected_efficiency) × scoring_weight
```
Volume and efficiency get **opposite treatment**, and this is the core insight:

- **Volume is predictable.** Target share, snap share and carry share are stable year to
  year. Project them from role, depth-chart rank, and team environment; lean on them.
- **Efficiency is noisy.** Yards per target, catch rate and — above all — **touchdown
  rate** are close to random over a season. Regress them hard toward positional means.

Most fantasy mispricing is unregressed touchdown luck, which is exactly what
`ff_opportunity`'s `*_exp` columns expose. A player whose actual TDs badly exceed expected
TDs is a sell; the consensus board frequently is not pricing that.

## Acceptance Criteria

### Implementation
- [ ] `int_projected_volume` — targets/carries/attempts from role × team environment
- [ ] `int_projected_efficiency` — rate stats regressed to positional mean, shrinkage
      strength a documented `var`
- [ ] `fct_player_season_projection` — grain player × season × scoring_format,
      contract enforced, portable types
- [ ] **rookies get a projection**, from draft capital + depth-chart role. This closes
      the 15 blanks on the current board (Jeremiyah Love at pick 41 among them).
- [ ] `projected_position_rank`, and the headline metric **`edge_vs_adp`** — computed on
      **within-position ranks** (the raw gap is a positional artifact; see S016)
- [ ] a **corroboration flag**: does our structural projection agree with ECR's direction
      against ADP? Agreement is the high-confidence buy; disagreement is where consensus
      likely knows something we cannot see
- [ ] carry **both** uncertainty signals — `ecr_stddev` (expert disagreement) and ADP
      `stdev` (crowd disagreement). They are different populations, not interchangeable
- [ ] every projection carries an **interval or confidence tier**, not just a point
      estimate. A point estimate implies precision the model does not have.

### Validation
- [ ] scored by the **S017 harness**; must beat baselines 1 and 2 to ship
- [ ] result vs. baseline 3 (ECR) **recorded honestly in the story**, whichever way it goes
- [ ] contract holds; grain unique; `dbt build` green on sample and full history
- [ ] spot-check: projected top-12 at each position is not obviously wrong

## Definition of Done
A projected 2026 season exists for every draftable player including rookies, it beats the
naive baselines by the S017 harness, and the draft board is rebuilt on our own ranking.

## Known limitation to state plainly when it ships
The model sees box scores, Vegas lines and depth charts. It does **not** see camp
reports, scheme changes, holdouts, or coach comments — which is much of what moves
consensus. Expect it to disagree with ECR most where consensus knows something we
structurally cannot. Those disagreements are the ones to check by hand, not to trust.
