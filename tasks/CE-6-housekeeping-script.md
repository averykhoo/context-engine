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
updated: 2026-10-13a
closed:
---

Build step 5 (FRAMEWORK §6.11): baton expiry into tasks; stale `kind: open` stubs into
`kind: abandoned` plus a baton; regenerated indexes; floor ratchets; `last_asked` stamps; the
`hk_` MCP set, including `hk.close` (AC-20). Runs from the gate and from a SessionStart hook.

## Read first

- `docs/framework/FRAMEWORK.md` §6.11, §8.4 (G-W9 to G-W11)
- zanzibar's scripts/task.py, function write_op (the `--mechanical` flag, and why close has none); another repo, so not a `file::symbol` here (G-D3)

## Log

- 2026-10-08d (claude-code/claude-opus-5-5): CE-2 left G-W11 here (DEC-14 item 5): marking a dead `kind: open` stub `abandoned` and its window, which needs measured session lengths (G-D9). `ce baton expire` already exists as the first hk_ operation.
- 2026-10-12b (claude-code/claude-opus-5-5): owns ledger rotation (FRAMEWORK 7.1), by trial (11.4); from the CE-16 coverage map
- 2026-10-12e (claude-code/claude-opus-5-5): Seen 2026-10-12e: the session committed its work (ab0b155..49e8e55) and then its conversation was cleared without a close, leaving its kind: open stub. The provisional rule (stale after 2 or more closes or pauses) could not fire at the next start: no session had closed since. The owner had the next conversation adopt the key and close it (2026-10-13). An adopt-and-close route (work committed, trailers present) belongs beside abandoned in the G-W11 design.
- 2026-10-13a (claude-code/claude-opus-5-5): Owner, DEC-29: marking a stale stub abandoned stays by hand for now (the owner sees open sessions at every start, US-16). When built: the window is 3 later closes or pauses, counted from the session's LAST ACTIVITY (its newest op in docs/ledger/ops.jsonl, which resets on any write), not from its opening; orient's open-sessions line shows last active. A read-only live session writes no op: consider a cheap touch op.
