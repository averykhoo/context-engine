---
type: Task
id: CE-169
title: Ledger rotation by period once a ledger cap is set (FRAMEWORK 7.1, by trial 11.4)
brief: Set a ledger cap with provenance, then rotate the session ledger by period with an index; every ledger reader follows
pri: SOMEDAY
state: open
deps: []
goals: [G-3]
source: session 2026-11-01b
created: 2026-11-01
moved: 2026-11-01b
updated: 2026-11-01b
---

Split out of CE-6 by DEC-138: FRAMEWORK §7.1 adopts rotation by trial (§11.4) once a ledger cap is set, and none is set. Rotation touches every ledger reader. Measured 2026-11-01: docs/ledger/session-log.md 88,886 bytes, 76 entries; the op log is not covered by §7.1.

## Traps

## Read first

- FRAMEWORK §7.1, §11.4; CE-6's log

## Log
