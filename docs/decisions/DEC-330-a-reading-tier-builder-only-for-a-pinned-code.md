---
type: Decision
id: DEC-330
title: A reading-tier builder only for a pinned code task that changes neither FRAMEWORK nor the contract
tasks: [CE-219]
actor: claude-code/claude-opus-5-5
decided: 2026-11-11
session: 2026-11-11a
decision_status: ACCEPTED
body_sha: sha256:d56d81bd38468c5e289f48b4e52575f5d7b0b3e9c5a3b51cf164b4a36a67fb1c
---

**Decision:** Above the size floor, a builder runs on the reading tier (sonnet here) only for a code task whose planner-pinned design leaves no open question and which changes neither FRAMEWORK.md nor the contract; this is DEC-177's filter. A design is pinned when it names every file's change and every test and leaves no call to the builder and no ASK raised for the task. Docs-only tasks above the floor, FRAMEWORK or contract tasks and unpinned designs keep a most-tier builder (opus).

**Why:** DEC-326 adopts sonnet builders for "code tasks whose plan pins the design"; DEC-177 kept FRAMEWORK and contract builds on opus; the CE-198 trial's evidence covers only code tasks. The kit's runbooks are not excluded from a reading-tier build (DEC-177 dropped the advice's kit exclusion), but they are above the floor by its third check.

**Rejected:** reading-tier builders for docs-only tasks or for FRAMEWORK and contract changes (no evidence from the trial).

Planner's call for CE-219, session 2026-11-11a.
