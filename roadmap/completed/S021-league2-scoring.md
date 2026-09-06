# S021 — Second league scoring: verified, not assumed

**Phase**: 1 — follow-up to S005E
**Functional unit**: the second league's rulebook → confirmation, and an honest label

## Outcome
**No code change to the scoring.** The second league's rules were diffed line by line
against all four seed formats, and `ppr` is an **exact match on all 11 scored stats**:

| | League 2 | seed `ppr` |
|---|---|---|
| passing_yards | 0.04 | 0.04 |
| passing_tds | 4 | 4 |
| interceptions | −2 | −2 |
| rushing_yards | 0.1 | 0.1 |
| rushing_tds | 6 | 6 |
| **receptions** | **1** | **1** |
| receiving_yards | 0.1 | 0.1 |
| receiving_tds | 6 | 6 |
| fumbles_lost | −2 | −2 |
| special_teams_tds | 6 | 6 |
| two_point_conversions | 2 | 2 |

The `PPR` tab was right for this league all along. That was **luck, not method** — it had
never been checked, and the identical assumption was wrong for the kiddy league.

## What actually changed
The label. The tab read *"PPR — generic, not a league's real rules"*, which is now false.
It reads **"Other league rules — full PPR, 4-pt passing TDs"**. `half_ppr` and `standard`
stay marked generic, because no league in play uses them.

## Why the two leagues differ so much
Same platform, opposite settings on the three rules that matter most:

| | Kiddy | Other |
|---|---|---|
| Receptions | **0** (standard) | **1** (full PPR) |
| Passing TDs | **6** | **4** |
| Fumbles lost | 0 | −2 |
| Return TDs to player | no — D/ST only | **yes** |

The return-TD split is the subtle one and it is readable from the rulebooks: the kiddy
rules have **no Miscellaneous section**, while league 2's lists return TDs *and*
`Total Fumbles Lost` — a line a team defense cannot record. Miscellaneous is ESPN's
individual-player scoring, so in league 2 the returner is paid and in the kiddy league he
is not. James confirmed the kiddy half independently.

## Accuracy of each board
- **Other league — exact.** Every scored line is priced, there are **no long-TD bonuses**,
  and the `ppr` format already reconciles to **zero disagreement against nflverse's own PPR
  across 23,510 player-weeks**. The numbers are not an approximation.
- **Kiddy league — exact except the +3 long-TD bonuses**, measured at ≈0.27 ppg for QBs and
  ≈0.11 for WR/TE (S020).

Six lines in league 2 go unpriced — `Fumble Recovered for TD`, `Interception Return TD`,
`Fumble Return TD`, `Blocked Punt or FG return for TD`, `2pt Return`, `1pt Safety`. All are
recovery/defensive scores that a QB/RB/WR/TE effectively never records. Not worth modelling.

## Acceptance Criteria
- [x] league 2 rules diffed against every seed format, programmatically rather than by eye
- [x] tab labelled with the league it actually serves
- [x] remaining generic tabs still marked generic
- [x] unpriced lines enumerated and justified rather than ignored

## Definition of Done
Both leagues are served by verified rules, and no tab claims rules it was never given. ✅
