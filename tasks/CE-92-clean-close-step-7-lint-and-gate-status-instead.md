---
type: Task
id: CE-92
title: 'Clean close step 7: lint and gate status instead of a second full gate run (dedupe-1, DEC-49)'
brief: Only records change between close steps 2 and 7; the code scope is still green (G-V1), and the gate already runs lint
pri: LATER
state: open
deps: []
source: session 2026-10-15c
created: 2026-10-15
moved: 2026-10-15c
updated: 2026-10-15c
---

DEC-49 approves dedupe-1. procedures.md § Clean close step 7 says "Lint and `<gate>` again", and step 2 has already run the gate, which embeds lint. Between them, the close writes only records (ledger, banner, board), which are outside the code scope.

Change step 7 to `context-engine lint` plus `context-engine gate status --require code`, with a full gate run only when status says the scope's id moved. Keep step 1's lint: it is a baseline taken before the session's own writes. The same change goes into FRAMEWORK §6.3 item 7, the kit copy of procedures.md (byte-equal), manual-mode if it says so, and the clean-close skill's quotes. A repo without `[gate]` keeps the full re-run.

## Traps
- A kit runbook edit: wait for the CE-7 hold to lift, or ask.
- The skill quotes and kit copies are byte-checked by the gate: edit them together.
- Sabotage: show a close whose code changed after step 2 still forces a re-run.

## Read first
- docs/runbooks/procedures.md § Clean close
- docs/framework/FRAMEWORK.md §6.3, §8.5 G-V1
