---
type: Decision
id: DEC-333
title: The roster gains a planner row; a new criterion pins the build ladder
tasks: [CE-219]
actor: claude-code/claude-opus-5-5
decided: 2026-11-11
session: 2026-11-11a
decision_status: ACCEPTED
body_sha: sha256:9831bf8a93b1545334dd1fd06b695d8f380291457e4b500e35f797ce31d8b6e5
---

**Decision:** FRAMEWORK §6.6's roster gains a planner row (one agent per task above the size floor, before any builder; most tier; writes nothing; returns the design). The builder row's Model cell names the reading tier for a pinned code build and the most tier otherwise and for every fix after the second FAIL. AC-113's text names the planner, and a new criterion, from DEC-173, DEC-177 and DEC-326, pins the size floor and the build ladder (tests/test_roster.py).

**Why:** the roster is meant to define every role the session delegates (AC-113), and since DEC-177 every task above the floor has a planner. The ladder is a new rule traced to DEC-173, DEC-177 and DEC-326, so it gets its own criterion rather than widening AC-113, which is the roster's shape (DEC-18, DEC-44).

**Rejected:** folding the ladder into AC-113.

Planner's call for CE-219, session 2026-11-11a.
