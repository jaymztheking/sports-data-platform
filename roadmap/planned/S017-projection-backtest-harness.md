# S017 — Projection backtest harness

**Phase**: 2 — Our own projections
**Functional unit**: feature marts + historical actuals → scored accuracy report

> **Deliberately before the model.** Rule 2 is TDD-first, and a projection without a
> backtest is an opinion with extra steps. This story builds the scoreboard; S018 builds
> the thing being scored.

## User Story
As the person deciding whether to trust these projections, I want every candidate
projection scored against history and against the alternatives, so that "our model is
better" is a measurement rather than a claim.

## Scope
Train/test split, baselines, metrics, leakage guard. No projection logic — S018.

## Acceptance Criteria

### Implementation
- [ ] Train on **2022–2024**, test on **2025**. Split is a `var`, not a hardcode.
- [ ] **Leakage guard** — an explicit test that no feature for season *N* is computed
      from season *N* data. This is the single easiest way to produce a model that
      backtests beautifully and fails live.
- [ ] Baselines, in increasing difficulty — a projection must beat 1 and 2 to be worth
      shipping, and matching 3 is the real bar:
      1. **Last season's per-game points** (what `fct_player_season` does today)
      2. **Positional average** by depth-chart rank
      3. **ECR itself** — consensus is strong; matching it is a genuine result
- [ ] Metrics: **MAE** and **RMSE** on per-game points, plus **Spearman rank
      correlation**. Rank correlation is the one that matters — drafting is an ordering
      problem, and being wrong about everyone by a constant costs nothing.
- [ ] Report scored **by position** and **by tier** (top-24 / 25–60 / rest). A model that
      is excellent on scrubs and poor on first-rounders is worse than useless.

### Validation
- [ ] harness runs on the committed sample and on full history
- [ ] baselines reproduce known values (the 2025 board is the fixture)

## Honest expectation
Beating ECR is hard — it aggregates dozens of analysts with information we do not have
(camp reports, injury nuance, coach interviews). **Target: match ECR on rank correlation,
clearly beat last-year's-points.** If the first structural model lands between baselines
2 and 3, that is a success, not a failure.

## Definition of Done
Any projection can be scored against three baselines on four metrics, sliced by position
and tier, with leakage proven absent.
