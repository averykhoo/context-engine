---
type: Task
id: CE-144
title: G-D3 fails an ambiguous bare file name only when the matching files differ (CE-89 item 3)
brief: Optional (owner may drop it); byte-equal kit and repo copies cited by bare name (AC-71) must keep passing
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-23f
updated: 2026-10-23f
---

G-D3 fails an ambiguous bare file name only when the matching files differ

CE-89's item 3, refiled on its own (items 1 and 2 landed in c5b812f). Optional. CE-41's brief asked G-D3 to fail a bare file name that matches more than one file; it was not built because AC-71 cites the byte-equal kit and repo runbook copies by bare name. If wanted, fail only when the matching files differ. Filed in session 2026-10-23f; the owner may drop it instead.

## Traps

- The kit/repo runbook copies (`docs/runbooks/*.md` and `src/context_engine/kit/docs/runbooks/*.md`) and `docs/framework/contract.md` / kit `contract.md` are byte-equal pairs cited by bare name; they must keep passing.
- `build/lib/` holds stale kit copies; it is gitignored, and `guards.py::Files.named` already drops ignored files.

## Read first

- CE-89 (item 3), CE-41
- `guards.py::Files.named`, `guards.py::links`; FRAMEWORK §8.3 G-D3; `docs/criteria.md` AC-71
- `.scratch/ce-93/build.md` (§ CE-89; gitignored, so the item is restated above)

## Log
