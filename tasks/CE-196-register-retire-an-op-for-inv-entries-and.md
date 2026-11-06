---
type: Task
id: CE-196
title: 'Register retire: an op for INV entries, and register show shows retired:'
brief: no op retires an INV entry; register show hides retired:, so a retired entry reads live
pri: LATER
state: open
deps: []
goals: [G-3]
source: session 2026-11-06f
created: 2026-11-06
moved: 2026-11-06f
updated: 2026-11-06f
---

Register retire: an op that retires a residual-risk register entry, and `register show` that shows `retired:`

Today a register entry (INV-n) is retired by hand: no op retires one, and `register show` hides
the `retired:` line, so a retired entry reads as live (INV-97 was retired this way, 2026-11-06).
This fact lived only in the HANDOFF banner until CE-195 cut the banner to durable lines
(verify-2, 2026-11-06f); it is filed here so it is not lost.

## Traps

- CE-49 is about retiring a story, not a register entry.

## Read first

- `docs/ledger/session-log.md` (the INV-97 retire), the register (`context-engine register show`)

## Log
