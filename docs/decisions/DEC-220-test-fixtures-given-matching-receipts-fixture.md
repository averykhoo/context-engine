---
type: Decision
id: DEC-220
title: 'Test fixtures given matching receipts: fixture ledgers and receipts() quote a pass count rather than opting out of the default, so the suite runs under the shipped default'
tasks: [CE-192]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:a75c0533906f7a617d44364d36f6354f89ff0ccb3feae5dc46f2f0473cb7b90b
---

The agent's call on CE-192: what the test suite does about fixtures whose closes' `guards:` receipts carried no pass count once the default turned on.

The fixture ledgers and the `receipts()` helpers were given receipts that quote a pass count (e.g. `gate 3 passed`), rather than opting each fixture out with `gate_receipt = ''`. Opting out would hide the shipped default from the suite, the very failure DEC-162 rules against. Only a test whose receipt text is its point sets `gate_receipt = ''` in its own config (the AC-125 off half).

Cost to undo: cheap.
