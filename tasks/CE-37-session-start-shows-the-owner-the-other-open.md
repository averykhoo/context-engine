---
type: Task
id: CE-37
title: Session start shows the owner the other open sessions
brief: "US-16: the owner sees every other open session at start; the session stops or closes none without the owner's word"
pri: NEXT
state: open
deps: []
source: session 2026-10-12e
created: 2026-10-13
moved: 2026-10-12e
updated: 2026-10-12e
review: [shipped]
---

US-16. orient already lists other open ledger stubs (Working.orient in working.py), but only to the agent: no ritual step shows them to the owner. Add the step to rituals.md § Session start (both copies), the orient heading, manual-mode § orient (both copies), FRAMEWORK §6.1, the kit contract and this repo's CLAUDE.md.

## Design review

affects: the owner, who reads one more section at every session start; every repo the kit deploys to, whose copied runbooks and contract gain the step
- reduced: a dead or forgotten session goes unnoticed because only the agent sees the list | rung: reduce | control: orient's heading itself says to show the owner, and the ritual row and both contracts repeat it; a test pins the heading
- reduced: a session stops, closes or abandons another session's stub on its own reading of the list | rung: reduce | control: the row says the session acts on none without the owner's word; abandon stays housekeeping's stale-window rule (G-W11)
- reduced: the owner cannot tell a live session from a dead one from the key alone | rung: reduce | control: each line carries when it opened, and the by-hand step adds its newest `Session:` commit
- residual: a repo that copied the kit before this change keeps the old runbook and contract | rung: collective | why: copied runbooks go stale on upgrade by design (INV-13) | control: the orient heading ships in the engine, so the instruction reaches them anyway
F: goes stale if orient's section order or the ledger stub format changes; the heading test catches a rename
A: by hand, read `kind: open` headings in the ledger and say them in chat (manual-mode § orient)
M: one heading string in Working.orient; prose rows in the runbooks, kept byte-equal by the gate
E: one more line in chat at start, "none" when there are none
