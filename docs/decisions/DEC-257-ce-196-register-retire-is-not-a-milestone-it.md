---
type: Decision
id: DEC-257
title: "CE-196: register retire is not a milestone: it rides along, DEC-36's list unchanged"
actor: claude-code/claude-opus-5-5
tasks: [CE-196]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:b487948d08d26390bd38e637268b94f2273211c3e9b5e48fc7a02a4a03be12fe
---

A build-time call for CE-196, the agent's own, PROVISIONAL until the owner reviews it.

`register retire` is not a milestone. Its write and its op line ride along to the next commit, as `doc freeze` and `doc archive` do. DEC-36's list of milestones, pinned by `tests/test_commit.py::MILESTONES`, is unchanged.
