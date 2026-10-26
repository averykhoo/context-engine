---
type: Question
id: ASK-21
title: 'CE-126: which fix for subagents sharing the session key, and when?'
brief: 'Recommended: B (op-line lane field), kept at LATER'
pri: NEXT
state: open
deps: []
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-23f
updated: 2026-10-26b
last_asked: 2026-10-26b
blocks: [CE-126]
---

## Question

CE-126: subagents share the coordinator's session key, so CE-125's per-session op-line split cannot tell their lines apart (seen 2026-10-23e: 8291569 "CE-133" carried baton.done BTN-5; 292541d "CE-133: close" carried comment CE-79). Which fix, and when?

## Options

- A. Sub-keys per subagent (e.g. 2026-10-23f.CE-126): heavy; SESSION_RE, ledger, Session trailer, foreign-commit reconciliation, orient, abandon, G-W7 all need parent/child rules.
- B. A lane field on each op line (CE_AGENT / --agent / MCP `agent`, set to the task id); commit selects by session and lane; session close takes every lane. Medium, additive, no migration: unlabelled lines are the coordinator's, as today. Fits one subagent, one task, one commit (DEC-60).
- C. The lane inside `actor` (claude-code/<model>+CE-126): least code, blurs provenance.
- D. No code: only the coordinator commits, or worktrees. Contradicts DEC-60; worktree builders gave false greens 2026-10-23a.

## Recommendation

B, kept at LATER for now (harm so far is mis-filed lines, not lost or half-committed work), with a one-line fan-out rule (pass CE_AGENT=<task id>) once B exists. Brief: .scratch/ce-126/brief.md (2026-10-23f), transcribed here.
