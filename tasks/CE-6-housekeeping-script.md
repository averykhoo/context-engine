---
type: Task
id: CE-6
title: "Tier-0 housekeeping script and the hk_ operations"
brief: "No model. Carries out recorded intent only; hk.close needs a verified Closes: trailer"
pri: NOW
state: open
deps: [CE-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-30a
updated: 2026-11-01b
closed:
goals: [G-3]
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
- 2026-10-13b (claude-code/claude-opus-5-5): Session-scope review 2026-10-13b (owner asked; fable consulted, .scratch/session-scope-ce/fable.md): (1) hk.close as specced has nothing to act on: the Closes: trailer rides only on the CE-n: close commit, which already wrote the task close (checked CE-30, CE-35, CE-36 on 2026-10-13a), so a task whose work is committed but never closed carries no trailer to verify. Redesign or drop hk.close; a Closes: trailer on a still-open task could be a lint red instead. (2) When G-W11 is built, the kind: abandoned entry should carry a derived digest (commits with Session: <key>, the Closes: lines, the op count from ops.jsonl), so a dead conversation loses only its prose judgement. Session scope itself stays per request (DEC-31); no per-task ledger entry.
- 2026-10-30a (claude-code/claude-opus-5-5): partial, integrated on main in 3fc1dbe (lane 1812238) with review fixes in f498178 (lane af963f2) and a test fix in 514affa: hk close (commit/ledger/--scan; a reopen outweighs an old trailer or old ledger rows) with the G-W9 lint, hk stamp (last_asked from asked receipts; G-W7 reads the op line's `as`) and the derived digest on abandoned stubs (AC-20, AC-165..167 tested; DEC-129, DEC-130). Residual for the close: G-W9 trusts a cited commit a shallow clone lacks (CI checkout is depth 1); hk close checks git at write time. Still owed: hk.ratchet (needs G-V2 floors), hk.comment, running tier 0 from the gate and the SessionStart hook, the G-W11 lint, G-W10 counts, adopt-and-close, a touch op for read-only sessions, ledger rotation.
- 2026-11-01b (claude-code/claude-opus-5-5): Owner, 2026-11-01b: "Finish ce6 now then push up ce11". Read as: finish CE-6 this session, then promote CE-11 to NOW.
- 2026-11-01b (claude-code/claude-opus-5-5): Lane ci integrated as 5858302 (cherry-pick of b97e93b): gate.yml checkout fetch-depth: 0 so G-W9/G-W11 read full history; tests/test_ci.py::test_the_workflow_checks_out_full_history_for_the_guards_that_read_it pins it (and linux_gate.py's full clone); AC-180 tested; gate.md + kit row. Live only on a push. Gate green on main (1359 passed). Left: guards.py::mechanical_closes docstring and FRAMEWORK §8.4 G-W9 still say a shallow clone is CI's checkout.
- 2026-11-01b (claude-code/claude-opus-5-5): Lane engine integrated on main (gate run green, 1382 passed, g1/code:6648aad35a101c86): d1984c7 LINT_IDS has every lint guard id, G-W9 (AC-168); 1624b6d one Closes: trailer per close in a multi-close batch (AC-169); 29eb511 session touch (AC-172); 9bdb909 G-W11 stale-stub lint (AC-173); 92c56bc hk comment (AC-174); 3ae496a hk run start|close and orient's Housekeeping owed (AC-175, AC-176); 80e9407 G-W10 counts and [housekeeping] max_writes (AC-177); dfe3848 adopt-and-close sentence in manual-mode; d14d51f FRAMEWORK 8.4 G-W9 full-history sentence; 87621ad FRAMEWORK names hk.ratchet and rotation not built; b16384a hk run commits only on a milestone write. Agent calls DEC-139..DEC-145. Open before close: coverage still reads G-W10 as deferred (frozen 2026-10-12 coverage map; G-W10 is not a lint id), so a newer coverage map or a recorded residual is owed.
