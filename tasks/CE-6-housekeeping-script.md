---
type: Task
id: CE-6
title: "Tier-0 housekeeping script and the hk_ operations"
brief: "No model. Carries out recorded intent only; hk.close needs a verified Closes: trailer"
pri: LATER
state: open
deps: [CE-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08a
updated: 2026-10-08d
closed:
---

Build step 5 (FRAMEWORK §6.11): baton expiry into tasks; stale `kind: open` stubs into
`kind: abandoned` plus a baton; regenerated indexes; floor ratchets; `last_asked` stamps; the
`hk_` MCP set, including `hk.close` (AC-20). Runs from the gate and from a SessionStart hook.

## Read first

- `docs/framework/FRAMEWORK.md` §6.11, §8.4 (G-W9 to G-W11)
- zanzibar `scripts/task.py::write_op` (the `--mechanical` flag, and why close has none)

## Log

- 2026-10-08d (claude-code/claude-opus-5-5): CE-2 left G-W11 here (DEC-14 item 5): marking a dead `kind: open` stub `abandoned` and its window, which needs measured session lengths (G-D9). `ce baton expire` already exists as the first hk_ operation.
