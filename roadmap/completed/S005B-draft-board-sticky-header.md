# S005B — Draft board: sticky header renders inside the table

**Phase**: 1 — Thin vertical slice (follow-up to S005A)
**Functional unit**: the published draft-board artifact — presentation layer over `fct_player_season`

> Filed 2026-09-06 on James's report, and fixed in the same pass because the draft was
> that day and the board was in live use. Written up as completed rather than planned.

## Bug
The column header row (`# / Player / Pos / Bye / ECR / …`) did not stay at the top of the
table. It rendered **between Ja'Marr Chase and Jahmyr Gibbs** — i.e. parked partway down,
overlapping rows one and two, instead of pinning above them.

## Root cause
A CSS overflow interaction, not a layout mistake:

```css
.tablewrap { overflow-x: auto; }          /* wide table scrolls in its own container */
thead th   { position: sticky; top: 53px; } /* 53px = guessed height of the controls bar */
```

Two compounding faults:

1. **`overflow-x: auto` silently creates a vertical scroll container too.** Per spec, when
   one overflow axis is not `visible`, the other computes from `visible` to `auto`. So
   `.tablewrap` became a scrollport in *both* axes, and the sticky header began resolving
   against **the wrapper** rather than the viewport.
2. **`top: 53px` was a magic number** — a hardcoded guess at the height of the sticky
   controls bar above. Since the wrapper had no bounded height it never scrolled
   vertically, so the header simply sat 53px down from the wrapper's top edge: on top of
   the first rows, permanently.

The `@media (max-width:640px){ thead th{ top:88px } }` override was a second guess layered
on the first, which is the tell that the approach was wrong rather than mistuned.

## Fix
Give the table a bounded scroll region it genuinely owns, and pin the header to the top of
*that* region — no magic numbers, no dependence on the controls bar's height:

```css
.tablewrap { overflow: auto; max-height: 72vh; }
thead th   { position: sticky; top: 0; }
```

Also switched the table to `border-collapse: separate`, since collapsed borders do not
paint reliably under sticky headers, and moved row borders onto `td`.

## Acceptance Criteria
- [x] header pins above row 1 at every scroll position
- [x] header stays correct at mobile widths without a per-breakpoint `top` override
- [x] horizontal scrolling for the wide table still contained; page never scrolls sideways
- [x] both themes unaffected; focus states intact

## Definition of Done
Header pins correctly, no hardcoded offsets remain, and the fix survives resize. ✅

## Note for future artifact work
The generated HTML lives only in the session scratchpad, not in the repo, so it was
regenerated from scratch to apply this. **If the draft board is going to be maintained,
its generator belongs in version control** — `scripts/` or an `analyses/` sibling — rather
than being rebuilt each time from a query plus a prompt. Worth a story before the next
in-season refresh.
