---
type: Task
id: CE-239
title: 'record waive: a per-record, per-text lint waiver for append-only bodies'
brief: one record, one guard, one exact text; never a whole guard, never text appended later (DEC-347)
pri: LATER
state: open
deps: [CE-238]
goals: [G-6, G-2]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

record waive: a per-record, per-text lint waiver for append-only bodies.

Carry out DEC-347. Lint runs G-D3 at rest over decision and story text above `## Amendments`, which an adopter may not edit, and nothing records a legal way out of a red there (docs/evidence/engine-feedback-2026-11-17.md, F32 and F31's residual 6). adhoc-microphone-array's formula `(M-4)(S-3) >= 6` (two decisions, three lines) reads as story citations under its one-letter `S` prefix; audio-workspace has 6 citations of sections their targets really lack.

1. A record op, working name `record waive <id> <guard> "<exact text>" --reason "<why>"`, appends an amendment in the shape the `corrected:` entries use (okf.py::correction_entry, okf.py::CORRECTED_RE), naming the guard, the exact text and the reason. It refuses text the record's body does not contain, a guard that cannot be waived, and a text the guard does not fail.
2. Lint reads those entries and skips that exact text, for that guard, in that record only (guards.py::record_refs first). An entry not in the op's shape, or naming text the body lacks, is red, as a hand-made `corrected:` entry is.
3. Runbooks: the op's by-hand step in manual-mode.md (DEC-20), and what the close digest says about a waiver; both runbook copies stay byte-equal.
4. Field check: dry lint in adhoc goes from 3 G-D3 lines to 0 after three waivers; audio-workspace's 6 likewise once CE-238 has landed.
5. Sabotage each refusal and the lint skip (DEC-11).

## Traps

- Never waive a whole guard for a record, and never text appended after the waiver: a later amendment repeating `(S-3)` is red again.
- The entry is op-owned: a hand edit to it, or a hand-written one, must be red, like a hand-made `corrected:` entry.
- Not grandfathering by body_sha or date, and not a math heuristic: DEC-347 rejected both. `[guards] allow_ids` is only an emergency fallback if this op slips; do not build it here.
- A waiver is a record write, cheap to undo: an agent may make it, and the close digest flags it (FRAMEWORK P8).
- Order: after CE-238, so the waivers cover only the true residue.

## Read first

- DEC-347; docs/evidence/engine-feedback-2026-11-17.md: F31, F32, § Second opinion item 3
- guards.py::record_refs, guards.py::added_refs, okf.py::insert_correction, okf.py::correction_entry
- docs/runbooks/manual-mode.md (the record correct steps)

## Log
