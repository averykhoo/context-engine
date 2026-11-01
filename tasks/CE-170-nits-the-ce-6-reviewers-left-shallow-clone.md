---
type: Task
id: CE-170
title: 'Nits the CE-6 reviewers left: shallow-clone docstring, hk.run signature, an untested dry branch'
brief: Small follow-ups from CE-6's 2026-11-01b review and verify; none blocks
pri: LATER
state: open
deps: []
goals: [G-3]
source: session 2026-11-01b
created: 2026-11-01
moved: 2026-11-01b
updated: 2026-11-01b
---

The CE-6 reviewers and final verifier (2026-11-01b) left these unaddressed; none blocked the close:

- guards.py::mechanical_closes's docstring still calls a shallow clone "(CI's checkout)"; CI fetches full history since 5858302.
- The hk.run signature in FRAMEWORK §8.0.2 and manual-mode § context-engine hk run leaves out `anyway`.
- The dry branch of working.py::Engine._hk_reindex has no test.
- working.py::Engine._comment_problem says "<id> is closed" for an id that is not a task.
- tests/test_ci.py's full-history test passes `fetch-depth: false` (Python's False == 0); harmless, since actions/checkout reads it as full history.
- The AC-180 row says G-W11 checks every cited commit; G-W11 counts ledger closes and pauses (working.py::Engine.stale_stubs), so the wording is loose.

## Traps

## Read first

- CE-6's close commit (b756f65) and log

## Log
