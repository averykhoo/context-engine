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
updated: 2026-10-08a
closed:
---

Build step 5 (FRAMEWORK §6.11): baton expiry into tasks; stale `kind: open` stubs into
`kind: abandoned` plus a baton; regenerated indexes; floor ratchets; `last_asked` stamps; the
`hk_` MCP set, including `hk.close` (AC-20). Runs from the gate and from a SessionStart hook.

## Read first

- `docs/framework/FRAMEWORK.md` §6.11, §8.4 (G-W9 to G-W11)
- zanzibar `scripts/task.py::write_op` (the `--mechanical` flag, and why close has none)

## Log
