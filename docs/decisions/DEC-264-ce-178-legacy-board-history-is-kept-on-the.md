---
type: Decision
id: DEC-264
title: 'CE-178: legacy board history is kept on the import op line (as), not exempted from G-W7; a later hand edit stays red'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-178]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:434d5c3a1f4d8ef4b6c8d198bf90648cbcbb8e574e42344271b2e99582254045
---

A build-time call for CE-178, the agent's own, PROVISIONAL until the owner reviews it.

A legacy board's history is kept on the import's op line, not exempted from G-W7. `task import` records each `moved`, `updated`, `closed` and `last_asked` value it writes in that record's op line `as` map, the field `guards.py::tool_owned` already reads for housekeeping's `last_asked` stamp (CE-6). G-W7's logic is unchanged: the file must hold the value the newest line that wrote the key recorded, so a later hand edit stays red.

Rejected: dropping the declared values from the line's `fields` so G-W7 falls back to "predates the op log" (it reds a legacy key newer than the log's first session, makes `fields` lie, and leaves nothing to compare a later edit with); G-W7 skipping records whose newest op is `import` (a hand edit after the import would pass).
