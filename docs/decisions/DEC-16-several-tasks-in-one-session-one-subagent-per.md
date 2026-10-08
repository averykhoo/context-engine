---
type: Decision
id: DEC-16
title: 'Several tasks in one session: one subagent per task, the top level only reports'
actor: owner
decision_status: PROVISIONAL
tags: '[delegation, subagents, framework]'
decided: 2026-10-09
session: 2026-10-09b
body_sha: sha256:56c15ec83ff97758a5aa8eb2355d85879ac591cc7042ea04c1c2241bdd2a72b1
---

Owner, in order:

- *"If I ask to get multiple tasks done in one session, make it so a sub agents does each task, sub sub agents or ultracode handles task work, and the top level conversation is mostly clear except for reporting on progress or blockers/delays"*
- (after the agent saved it to this repo's memory only and asked whether it should go in the global `CLAUDE.md`) *"As in it should apply to every repo using this context framework"*

So it is a framework rule (FRAMEWORK P11 and §6.6), deployed with the framework to every repo
that uses it, not a per-repo memory:

1. **A request carrying several tasks gets one subagent per task.** The task agent owns that
   task end to end.
2. **The task agent pushes the work down again**, to its own subagents or to a workflow
   (ultracode).
3. **The top-level conversation stays clear**: it reports progress, blockers and delays, and the
   close digest; nothing else.

The agent's readings, which the owner has not confirmed:
- A single-task request is unaffected.
- Task agents must be able to persist (not `Explore`), each to its own file (§6.6).
- Judgement stays with the session (P11): it verifies first-hand before a commit, a push or a
  record write, and owner words are still recorded at the top level, verbatim (§6.2).
- Tasks that touch the same files go to one agent or run in sequence: the disjoint-ownership
  rule of build rounds (§6.6) applies to task agents too.
