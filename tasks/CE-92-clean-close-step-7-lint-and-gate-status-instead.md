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
updated: 2026-10-15e
---

DEC-49 approves dedupe-1. procedures.md § Clean close step 7 says "Lint and `<gate>` again", and step 2 has already run the gate, which embeds lint. Between them, the close writes only records (ledger, banner, board), which are outside the code scope.

Change step 7 to `context-engine lint` plus `context-engine gate status --require code`, with a full gate run only when status says the scope's id moved. Keep step 1's lint: it is a baseline taken before the session's own writes. The same change goes into FRAMEWORK §6.3 item 7, the kit copy of procedures.md (byte-equal), manual-mode if it says so, and the clean-close skill's quotes. A repo without `[gate]` keeps the full re-run.

## Traps

- Released from the CE-7 hold by DEC-50 (2026-10-15e): no need to ask first.
- The skill quotes and kit copies are byte-checked by the gate: edit them together.
- Sabotage: show a close whose code changed after step 2 still forces a re-run.

## Read first
- docs/runbooks/procedures.md § Clean close
- docs/framework/FRAMEWORK.md §6.3, §8.5 G-V1

## Log

- 2026-10-15e (claude-code/claude-opus-5-5): DEC-50 (owner, 2026-10-15e): released from the CE-7 hold; it can start without asking.
