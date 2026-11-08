---
type: Decision
id: DEC-267
title: 'CE-178: a legacy value the schema does not take (a plain date in a session-key field) is refused naming line and id, never converted'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-178]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:a391d8c2c136973e147b96f4cf6b7d6b3e0f9723e8ef2c3759d6423b6a1f8e9d
---

A build-time call for CE-178, the agent's own, PROVISIONAL until the owner reviews it.

A legacy value the schema does not take (a plain date such as `2026-07-29` in a session-key field like `moved`) is refused by `task import`, naming its line and id; it is never converted (`2026-07-29` to `2026-07-29a` would invent data) and `type = "key"` is not widened (that would loosen every key-typed field of every kind). The remedy is a key of the repo's own, e.g. `legacy_moved`.
