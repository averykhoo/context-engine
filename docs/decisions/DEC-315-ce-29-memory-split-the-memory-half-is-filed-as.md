---
type: Decision
id: DEC-315
title: 'CE-29 memory split: the memory half is filed as its own task (or CE-29 kept open) so coverage does not report component 23 Memory as done'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:2e40d4b38dafae7679ecc567d8bdd06393fa24ea64163f7a7d8477ce76163a43
---

**Decision:** CE-29's memory half (coverage component 23, Memory) is the owner's call and is not built in this change. Before CE-29 closes, the memory half is filed as its own task with "Memory" in its title, or CE-29 is kept open with a comment, so `context-engine coverage` does not report component 23 as done (its coverage-map row names only CE-29). The builder does not close CE-29; the coordinator makes the board call.

**Why:** closing CE-29 whole would mark Memory done in coverage while no decision on it exists.

**Rejected:** closing CE-29 whole after the hazards half.
