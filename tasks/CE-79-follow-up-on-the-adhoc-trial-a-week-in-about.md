---
type: Task
id: CE-79
title: Follow up on the adhoc trial a week in (about 2026-10-21)
brief: "Due about 2026-10-21: score adhoc's sessions under the engine against CE-4, list engine errors, report keep/fix/stop"
pri: NEXT
state: open
deps: []
source: session 2026-10-14d
created: 2026-10-14
moved: 2026-10-14d
updated: 2026-10-20e
goals: [G-6]
---

Owner, 2026-10-14d, verbatim: "make a new task to follow up in about a week to see how the trial is going."

Due on or about **2026-10-21**, a week after CE-7's cutover started (2026-10-14d).

## What to check

- How many sessions have run in adhoc under the engine since the cutover, and whether each opened and closed through it (adhoc's ledger and op log).
- Score those sessions against the CE-4 baseline (`docs/evidence/adhoc-baseline-2026-10-11.md`): start and close cost, and what was forgotten or done by hand.
- Engine errors, refusals and by-hand fallbacks seen in adhoc: each one becomes a row here.
- INV-31's live probes: did orient appear on startup, resume, /clear and compaction.
- Whether adhoc's pinned engine env (DEC-41) needs an upgrade, and whether the worktree branch is ready for the owner's merge decision.
- Report to the owner in a few lines: keep going, fix first, or stop.

## Log

- 2026-10-14f (claude-code/claude-opus-5-5): 2026-10-14f: the trial has started (owner: "okay its running now"); the first real session in adhoc is running. Check back about 2026-10-21.
