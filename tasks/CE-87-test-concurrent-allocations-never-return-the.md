---
type: Task
id: CE-87
title: 'test_concurrent_allocations_never_return_the_same_id fails under load: a worker waits past the 30 s engine-lock timeout'
brief: 'Not a flake to re-run past: root-cause the timeout, the worker count or the lock'
pri: NOW
state: open
deps: []
source: session 2026-10-15a
created: 2026-10-15
moved: 2026-10-15a
updated: 2026-10-15a
---

CE-78 fix stage, 2026-10-15a: Windows full gate run 1 had 1 failure, tests/test_store.py::test_concurrent_allocations_never_return_the_same_id: a worker was held off the engine lock for more than 30 s while about ten python.exe from concurrent agents loaded the machine (the run took 58 min against 21 min unloaded). store.py, lock.py and the test were untouched by CE-78; alone the test passed 3 of 3, and the full re-run passed (764). Fan-outs (DEC-16, DEC-44) run several gates at once, so a load-sensitive test turns a coordinator's gate red. Find whether the 30 s timeout, the worker count or the lock's fairness is wrong.
