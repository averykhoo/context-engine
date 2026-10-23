---
type: Decision
id: DEC-75
title: G-I3 is a new guard for delegated rulings, not a clause of G-I2, and skips superseded decisions
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:b3c22574fcedc33aab4fd13e02081f2f0da25b30b6e761cae69b73105c9a61ea
tasks: [CE-113]
---

An agent's call under P8 (cheap to undo), made by CE-113's builder in session 2026-10-23f and landed in 21a88d9. Recorded afterwards from the builder's report (its PROVISIONAL call 4). Not owner words, and not a ruling on the owner's delegation.

**Call.** The delegated-ruling check is a new guard, G-I3 (`guards.py::delegated_rulings`, sharing `guards.py::delegation_problems` with the write-time refusals), not a clause of G-I2. It is on whenever `[working] decision` is set, and it skips superseded decisions, so the remedy (record the ruling again, then supersede the old record) clears it. The new guard id was made owned for G-D12 by a `task comment` on CE-113.

**Why.** G-I2 is story-only and is off unless `[guards] stories` is set, so a clause there would not run on decisions in most repos. Skipping superseded decisions is what lets the named remedy turn lint green without editing a frozen record.

Task: CE-113. Commit: 21a88d9.
