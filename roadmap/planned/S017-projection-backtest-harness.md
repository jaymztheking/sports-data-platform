# S017 — Projection backtest harness

**Phase**: 2 — Our own projections
**Functional unit**: feature marts + historical actuals → scored accuracy report

> **Deliberately before the model.** Rule 2 is TDD-first, and a projection without a
> backtest is an opinion with extra steps. This story builds the scoreboard; S018 builds
> the thing being scored.

## User Story
As the person deciding whether to trust this, I want to measure whether our structural
features actually identify **where the market (ADP) misprices players relative to what
ECR already knows** — so that "this finds value" is a measurement rather than a claim.

## Reframed: the baseline is ADP, not ECR
We are not trying to out-predict expert consensus. The question is narrower and more
answerable: **does the ECR-over-ADP gap predict outcomes, and do our features tell us
which gaps are real?**

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
      2. **ADP itself** — the market. Beating it is the actual goal.
      3. **The raw within-position ECR−ADP gap**, unaided by our features. If our
         structural work cannot improve on the naked gap, it is not earning its place.
- [ ] Metrics: **MAE** and **RMSE** on per-game points, plus **Spearman rank
      correlation**. Rank correlation is the one that matters — drafting is an ordering
      problem, and being wrong about everyone by a constant costs nothing.
- [ ] Report scored **by position** and **by tier** (top-24 / 25–60 / rest). A model that
      is excellent on scrubs and poor on first-rounders is worse than useless.

### Validation
- [ ] harness runs on the committed sample and on full history
- [ ] baselines reproduce known values (the 2025 board is the fixture)

## Data constraint that shapes this story
ADP history is available (FFC, 2022/2024/2025) and outcomes are already in
`fct_player_season`, so **ADP → outcome is fully backtestable today**. ECR history does
**not** exist — it is a live snapshot never captured. So ECR's marginal contribution can
only be validated *going forward*, from the first stored snapshot on.

That asymmetry is fine, and it sets the order of work: backtest structural features
against ADP mispricing on 2022–2025 now; validate the ECR overlay from 2026 onward.

## Honest expectation
The measurable win is modest and real: identify which ADP-vs-consensus gaps hold up. Do
not expect a large edge — 8,000-draft ADP is a strong aggregate. A feature set that
reliably picks the right side of the gap slightly more than half the time is worth having.

## Definition of Done
Any projection can be scored against three baselines on four metrics, sliced by position
and tier, with leakage proven absent.
