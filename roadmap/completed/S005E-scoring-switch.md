# S005E — Draft board: switch scoring in the page

**Phase**: 1 — follow-up to S020
**Functional unit**: the published draft-board page — one board, two leagues

## Problem
S020 scored the board to the kiddy league's real rules, which was correct for that league
and left the **other** league unserved. The generator's `--scoring` flag produced a second
HTML file, but a second file needs a second artifact URL and a second thing to keep
refreshed — for what is the same 180 players with different arithmetic applied.

## Fix
The mart already carries **every** scoring format at
`player x season x scoring_format`. So the page now embeds all of them and switches
client-side.

Identity, ECR and bye are format-independent and stored once; only the scored figures
(`ppg`, floor, ceiling, swing, games, value, career ppg) vary per format. Switching is a
re-read of an in-memory block, not a rebuild.

- `Kiddy | PPR | Half | Std` control next to the position filter
- header states which rulebook is in force, and **labels the generic formats as generic** —
  the only rules we actually know are the kiddy league's
- `--scoring` now chooses the *default* selection rather than the only output

Cost: 52 KB → 101 KB. Irrelevant against the 16 MB artifact limit, and it removes a whole
publishing path.

## Why the generic formats are labelled that way
Every board before S020 was PPR because PPR is the common default — and the kiddy league
turned out to be standard. The label (`"PPR — generic, not a league's real rules"`) exists
so that the same silent substitution cannot happen again: if the second league's board is
being read off the `PPR` tab, the header says out loud that those are assumed rules.

## Acceptance Criteria
- [x] all four formats switch without a rebuild; sorting follows the active format
- [x] floor/ceiling bars rescale per format (they are scaled within position)
- [x] rookies stay `no 2025 data` in every format rather than becoming 0
- [x] header names the active rulebook and flags generic ones
- [x] cross-off state is preserved across a format switch — it is about players, not scoring
- [x] ruff, ruff-format, mypy clean

## Still open: the second league's rules are unknown
The `PPR` tab is an **assumption**, exactly as the kiddy board was until James supplied the
settings. Reading the other league's rulebook the same way would take minutes and would
either confirm the tab or add a fifth format.

## Definition of Done
One artifact serves both leagues, and no board silently claims rules it was never given. ✅
