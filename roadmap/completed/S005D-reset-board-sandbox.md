# S005D — Draft board: Reset board did nothing

**Phase**: 1 — follow-up to S005C
**Functional unit**: the published draft-board page

## Bug
**Reset board** was inert. Clicking it produced no dialog, no error, and no change.

## Root cause
`window.confirm()` in a sandboxed frame.

Artifacts render inside an iframe whose `sandbox` attribute does not include
`allow-modals`, so `confirm()` never opens a dialog and **returns `false`**. The guard
therefore read as "user declined" on every click:

```js
if (confirm('Clear all ' + drafted.size + ' drafted players?')) {
    drafted.clear(); save(); render();   // never reached
}
```

Nothing threw, so there was no console error to notice — the fail mode is silence.

The irony is that S005C already guarded `localStorage` for exactly this reason: sandboxed
frames restrict browser APIs. The lesson was applied to storage and not to modals, because
`confirm()` did not *look* like a capability — it looked like plain JavaScript.

## Fix
Two-step confirmation entirely in-page, no browser modal:

- first click **arms** the button — label becomes `Tap again to clear N`, turns red
- second click within **4s** clears; otherwise it disarms itself
- button is **disabled** and reads `Nothing to reset` when nothing is crossed off, so an
  empty board looks inert on purpose rather than broken

Destructive-action protection is preserved without depending on a blocked API.

## Acceptance Criteria
- [x] reset actually clears the board, and clears persisted state
- [x] a single stray click cannot wipe a live draft
- [x] no `confirm` / `alert` / `prompt` anywhere in the generated page
- [x] empty state is visibly inert rather than silently dead
- [x] `aria-live` on the button so the armed state is announced

## Rule for future artifact work
**Assume the sandbox denies anything that interrupts or escapes the frame.** Modals
(`alert`/`confirm`/`prompt`), `window.open`, cookies, top-level navigation. Storage is
allowed here but still worth guarding. Build interaction in-page; if a browser capability
must be used, it needs a working fallback, because the failure is silent rather than loud.
