# S005C — Draft board: cross off drafted players

**Phase**: 1 — follow-up to S005A
**Functional unit**: the published draft-board page — live-draft state tracking

## User Story
As someone drafting live, I want to strike a player off the board the moment he is taken,
so that what is left on screen is what is actually still available.

## Scope
Click-to-cross-off, persisted locally. No league sync, no draft-order import, no multi-user
state — the board is a personal cheat sheet, not a draft room.

## Acceptance Criteria
- [x] click any row to toggle drafted; **whole row is the hit target** — a pick clock is no
      place for precision clicking
- [x] **persists across a page refresh** (`localStorage`). Losing the board mid-draft to a
      stray reload would make the feature worse than useless
- [x] every storage access guarded — the page still works if storage throws in a sandboxed
      frame, just without persistence
- [x] drafted rows are struck through and dimmed but **deliberately still legible**:
      mid-draft you need to check who went, and undo a misclick
- [x] **Hide drafted** collapses them out; **Reset board** clears all, behind a confirm
      (destructive mid-draft)
- [x] live **Available / Drafted** counters in the header tiles
- [x] keyboard accessible — rows focusable, Enter/Space toggles, `aria-pressed` on the box

## Also in this story: the generator is now in version control
`scripts/build_draft_board.py` builds the page from `int_draft_board` + `fct_player_season`.

Flagged in S005B and fixed here. The page previously existed only in session scratchpad, so
a one-line CSS fix meant regenerating the whole thing from a query plus a prompt — and the
file had already been lost once. It is now reproducible:

```
uv run python -m nfl.ingest.ff_rankings
NFL_DATA_DIR=data/raw NFL_DUCKDB_PATH=nfl_dev.duckdb uv run dbt build ...
uv run python scripts/build_draft_board.py
```

Output goes to `build/` (gitignored) — the HTML is a build artifact, the generator is source.

## Definition of Done
Players cross off in one click, survive a refresh, and the page rebuilds from a committed
script. ✅

## Deliberately not done
- **No league sync.** Pulling actual picks from ESPN would remove the manual step, but it
  needs league auth and a polling loop — a real story, not a footnote to this one.
- **State is per-browser.** Two drafts on two devices do not share a board. Fine for one
  person; worth knowing before relying on it.
