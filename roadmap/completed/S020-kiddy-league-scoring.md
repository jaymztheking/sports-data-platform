# S020 — Kiddy league scoring

**Phase**: 1 — follow-up to S005A
**Functional unit**: real league rules → `scoring_rules.csv` → every downstream mart

## User Story
As someone in the kiddy league, I want the board scored to my league's actual rules, so
that the rankings describe my league rather than a generic one.

## What the rules turned out to be
Supplied by James 2026-09-06 from the ESPN settings screen. Two differences from what the
board was using, and both matter:

1. **There is no reception scoring.** No "Each Reception" line anywhere in the rules — the
   league is **standard**, not PPR. The board had been published in PPR throughout.
2. **Passing TDs are worth 6**, not the ESPN default of 4 that the seed carried.

Smaller ones: **no offensive fumble penalty** (the seed had −2), and 2-pt conversions at 2,
which already matched.

## Effect on rankings (2025 production, draftable pool)

| Position | avg rank shift | max |
|---|---|---|
| WR | 3.7 | 12 |
| RB | 2.9 | 12 |
| TE | 2.5 | 6 |
| QB | 1.4 | 3 |

Movement is exactly the shape dropping PPR should produce, which is the sanity check:

- **Up** — deep threats and TEs: DJ Moore +12, Terrance Ferguson +11,
  Jacory Croskey-Merritt +9, Josh Oliver +8, Darren Waller +7
- **Down** — possession receivers and pass-catching backs: Wan'Dale Robinson −12,
  Tyjae Spears −12, Keenan Allen −11, Kenny Gainwell −10, Alvin Kamara −8

QBs barely reorder because 4→6 points per passing TD lifts nearly all of them together.

## Acceptance Criteria
- [x] `kiddy` format added to `seeds/scoring_rules.csv`
- [x] `accepted_values` tests widened across marts / intermediate / seeds
- [x] `scripts/build_draft_board.py` takes `--scoring` and defaults to `kiddy`
- [x] board republished in league scoring; header states which rules are in force
- [x] `dbt build` green on sample and full history (53/53)

## Not modelled, and why — measured rather than assumed
The league pays **+3 bonuses** for a 50+ yard TD pass, 40+ yard TD rush, and 50+ yard TD
reception. Those need play-level yardage, which the box-score feed does not carry. Measured
from 2025 play-by-play before deciding:

- 38 pass TDs of 50+ yards league-wide; 46 rush TDs of 40+
- **≈0.27 ppg** across draftable QBs, **≈0.11 ppg** across draftable WR/TE
- Most concentrated case is ~0.53 ppg (three QBs with three long TD passes each)

Second-order against rank gaps of several points per game, so it is deferred rather than
rushed. Implementable from `data/raw/pbp.parquet` when wanted — the ingest exists.

**Return TDs go to the D/ST, not the returner** — confirmed by James 2026-09-06, so
`kiddy,special_teams_tds` is **0**. Worth noting the trap: `special_teams_tds` was added to
the seed in S005A precisely to reconcile with nflverse's own PPR column, which *does* credit
the player. Correct there, wrong here — a scoring rule can be right for one definition and
wrong for another, and only the league's own rules settle it. The reconciliation test is
scoped to `scoring_format = 'ppr'`, so it still passes.

Affected 14 skill players in 2025, each losing 0.6–1.2 ppg. Small overall but not
cosmetic: **Tory Horton was the single biggest riser** under the earlier assumption (+12)
and drops off the risers list entirely once the points are removed. DJ Moore (+12) is now
the largest mover.

## Out of scope
Kicker and D/ST scoring is fully specified in the league rules but the mart covers
QB/RB/WR/TE only — those positions score a flat zero under an offense-only seed and would
rank as meaningless ties (see S005A).

## Definition of Done
The board is scored to the kiddy league's real rules, with the PPR variant still buildable
via `--scoring ppr` for the other league. ✅
