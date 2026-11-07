---
type: Decision
id: DEC-190
title: decision link's refusal of a non-criterion id names the first criteria_rows problem when lint cannot read part of the file
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:61f23a312b4852a40665c258cdb37be9f55ce35419bd42ca42c07179c339d6eb
---

The agent's call on CE-150, made while building it in session 2026-11-07e: what `decision link` says when it refuses a criterion id.

When the target is neither a record nor a criterion row and the criteria file has a table `guards.py::criteria_rows` cannot read, the refusal names the first problem lint reports ("; lint cannot read part of <file> (<problem>)"), so a row in a table with no `status` or source column is not mistaken for a typo. With no unread table the message is unchanged. The remedy text is unchanged.

Cheap to undo: a message suffix, pinned by the test for AC-40.
