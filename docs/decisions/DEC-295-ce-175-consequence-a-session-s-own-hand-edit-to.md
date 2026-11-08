---
type: Decision
id: DEC-295
title: "CE-175 consequence: a session's own hand edit to HANDOFF.md no longer rides its close's banner commit; the reply says so and the session commits HANDOFF.md by path"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:544653864afac72e39b832da86c9b2a25e220d62de984c73fa4ab596477f5e78
---

A consequence of the CE-175 banner-only commit, accepted: a session's own hand edit to HANDOFF.md no
longer rides its close's banner commit (`session close --banner`) or any banner milestone. The reply
names it ("HANDOFF.md: its banner only, so the hand edits beside it stay uncommitted ..."), and the
session commits HANDOFF.md by path (`context-engine commit HANDOFF.md -m ...`). The engine cannot tell
whose hand edit it is, so it treats every one the same.
