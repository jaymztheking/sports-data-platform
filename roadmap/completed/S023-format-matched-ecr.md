# S023 — The reported ECR was PPR, in every league

**Phase**: 1 — follow-up to S022
**Functional unit**: FantasyPros per-format consensus → format-matched ECR

## The question
> "The reported ECR is based on what scoring?"

PPR. Always. In every tab, including the standard-scoring kiddy league.

## Root cause
`stg_nfl__ff_rankings` filtered `ecr_type = 'ro'` (redraft overall) — and every one of
those rows comes from **`/nfl/rankings/ppr-cheatsheets.php`**. The ffverse mirror has no
standard and no half-PPR page at all; grep the 31 `fp_page` values and the only redraft
overall board is the PPR one.

So a standard-scoring league was being ranked against PPR consensus, and
`value_over_ecr` compared standard-scored production to a PPR-scored market.

**It is wrong at the first pick**, not in the noise:

| Scoring | Consensus #1 |
|---|---|
| STD | **Jahmyr Gibbs** (1.41) |
| HALF | Jahmyr Gibbs (1.55) |
| PPR | **Ja'Marr Chase** (1.58) |

## Second defect found on the way
`ecr_type = 'ro'` is **not one board**: it spans `redraft-overall` (525 rows) *and*
`redraft-idp` (192 rows). So `int_draft_board` carried 81 LB / 58 DL / 53 DB rows whose
`ecr` is on the IDP scale — Jordyn Brooks at 1.7 sitting beside Ja'Marr Chase at 1.5, two
incompatible rank universes in one column. The published board filtered to QB/RB/WR/TE so
it never surfaced, but anything consuming `int_draft_board` without a position filter
would have been badly wrong. S004's note that the `ro` filter was "load-bearing" was right
that a filter was needed and wrong about which one.

## Fix
New ingest straight from FantasyPros, one board per scoring format:
`src/nfl/ingest/fp_rankings.py` → `stg_nfl__fp_rankings` → `int_draft_board`, now grained
on **scoring_format × player_join_key × player_position**.

- `league_settings.csv` gains **`consensus_format`**, mapping a league's rules onto a
  published board — the kiddy league is standard-scoring, so it draws on STD. In the seed
  rather than hardcoded, because a league can adopt rules no board exists for.
- Uses **`rank_ave`** (averaged expert rank, the analogue of ffverse's `ecr`), never
  `rank_ecr` — that is an integer ordinal on a different scale, and mixing them once made
  a diff report 320 players "moved" when nothing had.
- Bonus: this source publishes **daily**. The ffverse mirror lagged it by two days.

## Result
Consensus is now format-specific end to end. Same player, different tabs:

| | kiddy / std | half | ppr |
|---|---|---|---|
| Jahmyr Gibbs | **1.4** | 1.6 | 2.5 |
| Ja'Marr Chase | 2.5 | 2.6 | **1.6** |

## Acceptance Criteria
- [x] every scoring format's consensus ingested, with tests mocking the HTTP layer
- [x] a layout change raises rather than silently yielding an empty board
- [x] `int_draft_board` grained on scoring format; IDP contamination gone
- [x] league → board mapping in the seed
- [x] 65/65 on sample and full history; 100 pytest; ruff, mypy, sqlfluff clean

## Note
`stg_nfl__ff_rankings` is kept — S007 snapshots it for ECR history, which this new source
has none of yet. It is no longer what the marts rank against.
