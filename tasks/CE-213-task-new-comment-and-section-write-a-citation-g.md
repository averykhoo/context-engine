---
type: Task
id: CE-213
title: task new, comment and section write a citation G-D3 fails; the next milestone commits HEAD lint-red
brief: refuse before the write (DEC-209), not at the milestone's commit
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

`task new`, `task comment` and `task section` write a citation lint G-D3 fails, and the next milestone commits it, so HEAD goes lint-red (found picking up audio-workspace feedback, CE-193).

**What happened** (2026-11-08, session 2026-11-07e): the CE-193 builder filed CE-208, CE-209 and CE-212 with `task new`. Their bodies named three of audio-workspace's question ids bare, and CE-212 cut a symbol name to a prefix that is not a symbol. Nothing refused the writes. The builder's next op, `record new decision` (DEC-316), is a milestone, and its auto-commit 856bd83 carried every op line HEAD lacked with the files they name, these three tasks among them. Lint on a clean `git archive` of 856bd83 failed G-D3 four times; the fixes were hand edits, committed after.

**At HEAD 856bd83:** the write-time twin of G-D3 (CE-183, DEC-205) runs only in the append-only writes: working.py::Engine._cites_known from `record new` and `ask answer`, working.py::Engine._entry_cites_known from amend, correct, retire and confirm. working.py::Engine.new, working.py::Engine.comment and working.py::Engine.section call neither. A milestone (working.py::_milestone, store.py::Store.milestone) commits without lint, by design (DEC-209); only working.py::Engine.commit runs working.py::Engine._lint_carried. A board item's body is not stamped, so it can be fixed after, unlike CE-183's case, but between the milestone and the fix HEAD is lint-red, and another session can build on it.

**The fix to design:** run the twin on the text `task new`, `task comment` and `task section` would write, refusing before the write, with the same remedy (backticks for another repo's id). Or decide this is not worth a refusal, since the body can be edited, and say so in a decision. Either way, test that `task new` with a bare unknown id is refused (or, if not, that the milestone after it is), and sabotage it.

## Traps

- DEC-209 ruled out lint before a milestone's commit: the refusal belongs before the write, not at the commit.
- INV-149 says the twin is stricter than lint for deprecated records; a task's own deprecated status may need the same care.
- The twin is off with G-D3 (`[guards] off`); keep that.

## Read first

- src/context_engine/working.py::Engine._cites_known
- src/context_engine/working.py::Engine._entry_cites_known
- src/context_engine/working.py::Engine.new
- src/context_engine/working.py::Engine.comment
- src/context_engine/working.py::Engine.section
- docs/decisions/DEC-205-write-time-g-d3-twin-for-append-only-text-ce.md
- docs/decisions/DEC-209-the-check-runs-before-the-write-not-as-lint.md
- tasks/CE-183-record-new-auto-commits-a-record-that-lint-g-d3.md

## Log
