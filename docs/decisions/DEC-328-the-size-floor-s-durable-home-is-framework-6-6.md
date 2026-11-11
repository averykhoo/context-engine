---
type: Decision
id: DEC-328
title: The size floor's durable home is FRAMEWORK §6.6; the frozen advice doc is not edited
tasks: [CE-219]
actor: claude-code/claude-opus-5-5
decided: 2026-11-11
session: 2026-11-11a
decision_status: PROVISIONAL
body_sha: sha256:9d7cd68d1e9ac156d42d6a2ce8e2f7455224bebd571389ff0bd3a93834741bf4
---

**Decision:** The frozen advice doc (docs/evidence/article-takeaways-advice-2026-11-07a.md) is not edited. The size floor DEC-173 adopted (four checks on a task's summed edits, plus the below-floor read-only review whose FAIL promotes the task) moves into FRAMEWORK §6.6 as its durable home, and CLAUDE.md stops pointing at the advice doc.

**Why:** CE-219's text asks for the advice doc to be updated "in place", but the evidence route is ACTIVE-PLAN, then FROZEN, and frozen provenance is never edited (CLAUDE.md § Rules). The floor's four checks were written out only there, so a durable rule lived in a frozen file; FRAMEWORK §6.6 is uncapped, generic and read by every adopting repo. DEC-173's title still names the advice doc, as history.

**Rejected:** editing the advice doc in place (frozen); a new evidence doc for the floor (a second home for a rule, and evidence is not where rules live).

Planner's call for CE-219, session 2026-11-11a.
