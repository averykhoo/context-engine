---
type: Task
id: CE-210
title: "fan-out.md: the harness can refuse a write-capable agent's Write; the on-return check binds every delegation (audio-workspace item 9)"
brief: "Kit runbook: edit the kit copy and this repo's copy together (byte-equal gate)"
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

fan-out.md: say the harness can refuse a write-capable agent's Write, and make the on-return check a step of every delegation (audio-workspace feedback item 9).

**What happened** (audio-workspace `docs/context-engine-feedback.md` entry 9, agent-raised, 2026-11-06): a `general-purpose` subagent's Write to its scratch report was refused by the harness ("subagents should return findings as text"); it returned the report in its message and the session persisted it on receipt. Two other agents in the same session wrote their files fine.

**At HEAD cb362ca:** the ask is mostly met. The kit's fan-out.md, § Delegating reading and auditing, already says "On return, check the file exists and is not short; if it is, write the returned report to it before doing anything else with it." The gap is the line before it, "Only an agent that can write files can persist (not `Explore`)", which implies a write-capable agent always can.

**The change:** say that the harness can refuse a write-capable agent's Write mid-run, so the on-return check binds every delegation, not only an `Explore` one.

## Traps

- Two copies: src/context_engine/kit/docs/runbooks/fan-out.md and docs/runbooks/fan-out.md are kept byte-equal and LF by the gate (CE-46); edit both together.
- A kit change: it reaches every adopting repo on its next upgrade, so it may warrant a line in docs/framework/RELEASE-NOTES.md.

## Read first

- src/context_engine/kit/docs/runbooks/fan-out.md
- C:/Users/user/PycharmProjects/audio-workspace/docs/context-engine-feedback.md entry 9

## Log
