---
type: Task
id: CE-222
title: 'Gate runbook: report what a clean checkout skips; run local-data tests in the main tree before push'
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-10b
created: 2026-11-10
moved: 2026-11-10b
updated: 2026-11-10b
---

Make the gate runbook name the tests a clean checkout skips (adhoc's layer-2 note, 2026-11-10; audit item 11). In adhoc, a fresh-clone gate skips about 180 tests that need local data, so a green clean-checkout or CI gate never runs them.

- Every green from a clean checkout or CI reports its skip count and why.
- Before a push, the tests that need local data run in the main tree as a separate step.

Changes: kit/docs/runbooks/gate.md § Running it (the docs/runbooks copy stays byte-equal, LF). Check whether tools/linux_gate.py and CI here skip anything for that reason, and say so in the item's close.
