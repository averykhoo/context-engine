---
type: Decision
id: DEC-332
title: 'The one trial metric kept: an `escalated:` task comment per escalation'
tasks: [CE-219]
actor: claude-code/claude-opus-5-5
decided: 2026-11-11
session: 2026-11-11a
decision_status: PROVISIONAL
body_sha: sha256:19b55cdcd52f1ceb538f6acc7ce620014d92de2a52a6170f90f5706efd14f76b
---

**Decision:** One metric is kept from the CE-198 trial: each escalation, logged as a task comment on the escalated task starting `escalated:` with the FAIL class (greppable across tasks/). No per-task token comments, and no automatic review threshold.

**Why:** summing subagent tokens per task was the costly part of the trial, and DEC-326 ended the trial. Escalation was the trial's drop signal and is free to log, since it happens only on the exception path. An automatic threshold ("2 escalations in the last 6 ladder tasks raises an ASK") is rejected for now: ladder tasks are not marked, so "the last 6" cannot be counted without a new label; the comments let a later reviewer count by hand.

**Rejected:** keeping the per-task token and FAIL-round comments; keeping nothing at all; an automatic threshold.

Planner's call for CE-219, session 2026-11-11a.
