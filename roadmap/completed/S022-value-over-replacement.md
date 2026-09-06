# S022 — Value over replacement: make the board actually rank

**Phase**: 1 — follow-up to S021
**Functional unit**: league lineup settings → replacement level → league-aware draft order

## The bug James found
> "The order of players didn't change at all. It recommends the exact same rankings
> completely irrespective of scoring format, custom or not."

Correct, and worse than a display default. The board's ordering column was
`overall = row_number() over (order by ecr)` — pure FantasyPros consensus rank, which is
**format-independent by construction**. Switching scoring tabs changed the numbers inside
the cells and never the row order. Every scoring fix from S020 and S021 was decorating a
ranking we did not produce.

## Why the obvious fix is wrong
Sorting by per-game points *does* respond to scoring format. It also produces garbage.
The kiddy top 15 by raw points:

> Stafford, Josh Allen, Drake Maye, Purdy, Lawrence, Mahomes, Hurts, Prescott, Goff,
> Caleb Williams, Herbert, Nix, Burrow, Daniel Jones, Lamar

Fifteen quarterbacks, zero overlap with consensus. **Raw points are not comparable across
positions.** With 6-point passing TDs every startable QB scores a lot, so "most points"
just means "quarterback".

## The fix
Value over replacement. A player is worth what he beats the *waiver-wire alternative* at
his position by — and that baseline is set by the league's lineup, which is why this could
not be built until the settings arrived.

`seeds/league_settings.csv` holds team count and starting slots. Both leagues are 12-team,
1 QB / 2 RB / 2 WR / 1 TE / 1 FLEX. FLEX is filled by the best remaining RB/WR/TE rather
than a fixed split, so it deepens whichever positions actually produce. Replacement is then
the best player at each position that nobody has to start.

### Replacement level, 2025

| | Kiddy | NYACL (PPR) |
|---|---|---|
| QB | **21.1** | 17.4 |
| RB | 7.8 | 11.3 |
| WR | 7.8 | 11.5 |
| TE | 6.7 | 10.5 |

The kiddy QB line is the whole argument in one number: **QB replacement is the highest of
any position**, so despite 6-point passing TDs, *no quarterback makes the top 12*. Elite
QB production is abundant, and abundance is worth nothing.

### The boards now genuinely differ

| Rank | Kiddy | NYACL |
|---|---|---|
| 1 | Jonathan Taylor (RB) | Christian McCaffrey (RB) |
| 2 | Christian McCaffrey (RB) | Puka Nacua (WR) |
| 3 | Bijan Robinson (RB) | Bijan Robinson (RB) |
| 8 | Puka Nacua (WR) | Ja'Marr Chase (WR) |
| 9 | Jaxon Smith-Njigba (WR) | **Trey McBride (TE)** |

Kiddy's top 10 is seven RBs — correct for non-PPR. NYACL's is balanced, with a TE cracking
the top 10 on scarcity. Overlap between the two top-10s is 7 of 10, in a different order.

## Acceptance Criteria
- [x] `league_settings` seed with team count and starting slots
- [x] replacement level per scoring format per position, FLEX allocated to best remaining
- [x] `replacement_ppg`, `points_over_replacement`, `vor_draft_rank` on the mart, contracted
- [x] board defaults to `vor_draft_rank`; `#` still sorts by consensus for comparison
- [x] board order **changes when the scoring tab changes** — the actual bug
- [x] 57/57 on sample and full history; sqlfluff clean

## Limits worth stating
- Replacement uses **2025 production**, so it is still backward-looking. It fixes
  *comparability across positions*, not the underlying "last season ≠ next season" problem.
  That remains S016–S018.
- Bench depth (16 vs 14 roster) is ignored. Deeper benches thin the waiver wire and would
  lower replacement slightly; the effect is second-order next to starter counts.
- K and D/ST are still unranked — the mart covers QB/RB/WR/TE only.

## Definition of Done
The board produces a ranking of its own, in each league's rules, and that ranking moves
when the rules move. ✅
