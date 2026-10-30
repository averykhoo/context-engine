---
type: Task
id: CE-139
title: "Residual-risk entry for G-I3's not-checked case: a delegated ruling with neither ruled_by nor ## Ruling"
brief: 'No register op exists: carry it as a residual line on this item and close it, or record why DEC-27 needs none'
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-30a
updated: 2026-10-30a
review: [guard]
status: deprecated
closed: 2026-10-30a
---

Residual-risk entry for G-I3's not-checked case

CE-113's verifier (verify-1, Non-blocking 4) and its builder both found that G-I3 has no residual-risk (INV-n) entry for what it cannot see: a delegated ruling recorded with neither `ruled_by` nor a `## Ruling` section looks exactly like an owner decision, so neither lint nor the write-time refusal can catch it. Filed in session 2026-10-23f.

The engine has no op that adds a register entry directly (`register` has only `show`); entries are filed by `task close` from an item's `- residual:` lines. So: decide whether DEC-27 requires an entry here; if it does, give this item a design review with a `- residual:` line (rung, why not eliminated, control: G-I3 plus the contract's "Who decides" rule) and close it, which appends the INV entry.

## Traps

- CE-113 is already closed, so its own close cannot file the residual; this item carries it.
- `task close` refuses an item whose design review lists a residual it cannot file; check `register show` after the close.

## Read first

- `.scratch/ce-113/verify-1.md` (Non-blocking 4) and `.scratch/ce-113/build.md` ("Not done / for the verifier"); both gitignored, so the finding is restated above
- FRAMEWORK §7.4 and §8.1 G-I3; `docs/runbooks/manual-mode.md` § task close (residual lines); DEC-27

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: CE-139: G-I3's not-checked case (a delegated ruling with neither ruled_by nor ## Ruling) is filed as a residual-risk entry through this item's design review (rung: individual; control: the contract's Who-decides rule and FRAMEWORK §6.5, with G-I3 covering every ruling that names ruled_by or holds ## Ruling). No code change; call recorded as DEC-90.

## Design review

affects: the owner, whose delegated call would read as their own frozen words; every later session that reads that decision as owner intent
- residual: a ruling made on the owner's delegation but recorded with neither `ruled_by` nor a `## Ruling` section reads as the owner's own decision, so neither G-I3 nor the write-time refusals of `record new` and `ask answer` can see it | rung: individual | why: the file then looks exactly like an owner decision; only the transcript shows that the owner delegated the call, and the engine never reads the transcript | control: the contract's "Who decides" rule and FRAMEWORK §6.5 (a delegated call is recorded with `ruled_by`, never as `actor: owner`); G-I3 for every decision that names `ruled_by` or holds a `## Ruling` section
F: re-read when G-I3, `ask answer` or the contract's "Who decides" rule changes; the session that changes them updates this entry
A: `context-engine register show` prints it; by hand, its `## INV-n` entry in src/context_engine/REGISTER.md
M: G-W13 keeps the entry in the register for as long as CE-139 is closed with this review
E: reuses G-I3's own "Not checked" wording (FRAMEWORK §8.1) and the register's entry format (§7.4)
