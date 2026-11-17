---
type: Task
id: CE-247
title: Lint fails C0 control bytes in routed docs and records
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

Lint fails C0 control bytes in routed docs and records.

adhoc-microphone-array (AD-112 item 26): C0 control bytes in tracked docs pass lint; there is no such check in guards.py, okf.py or store.py. docs/evidence/engine-feedback-2026-11-17.md, F26.

## Traps

- Tab, newline and carriage return are not the target: allow them (CRLF files exist in adopters).
- Name the file, line and byte, so the fix is one edit; a stamped record's body needs a record op, not a hand edit.

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F26
- guards.py (the doc guards), store.py::Store._validate

## Log
