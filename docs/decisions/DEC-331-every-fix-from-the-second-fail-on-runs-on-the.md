---
type: Decision
id: DEC-331
title: Every fix from the second FAIL on runs on the most tier; the verifier is never a fixer
tasks: [CE-219]
actor: claude-code/claude-opus-5-5
decided: 2026-11-11
session: 2026-11-11a
decision_status: ACCEPTED
body_sha: sha256:6cf743b52254a4743ee17c7d1bb0e8bfae6e6156dccad0b505445525c4973cd1
---

**Decision:** Escalation: the first FAIL's fix runs on the builder's tier; the fix after the second verifier FAIL, and every later fix, runs on the most tier (opus here), and the task stays there. The verifier is never the builder or a fixer, before or after an escalation.

**Why:** DEC-326 says a task "escalates to opus after 2 FAIL rounds". Reading that as "the fix after the second FAIL" keeps one cheap retry on the builder's tier and stops a reading-tier builder from looping. A verifier that fixes would check its own work (FRAMEWORK §6.6, the coordinator: verification goes to another agent than the one that did the work).

**Rejected:** escalating after the first FAIL (drops the trial's saving on a single slip); never escalating (a reading-tier builder can loop on a design it cannot carry).

Planner's call for CE-219, session 2026-11-11a.
