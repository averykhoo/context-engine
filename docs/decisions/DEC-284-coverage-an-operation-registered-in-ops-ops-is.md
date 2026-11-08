---
type: Decision
id: DEC-284
title: 'coverage: an operation registered in ops.OPS is owned for G-D12 and built for coverage; only unregistered ones (hk.ratchet) need a map row or a board item'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:7d9d71db62bffea455788a2cf660d6d62291765a8326f0d740c52e895139b347
---

The agent's call on CE-164 (session 2026-11-07e): an operation registered in `ops.OPS` (its name with the dot as an underscore, `hk.run` as `hk_run`) is owned for G-D12 and reads built in `context-engine coverage`, with the note "the engine registers it (`hk_run`)".

The registry is the truth of what the engine carries, so a map row per registered operation would be noise that goes stale. Only an unregistered operation needs a map row or a board item; today that is `hk.ratchet`, which open CE-168 names and the new dated map marks DEFERRED. A board item or map cell may name an operation in either form (`hk.run` or `hk_run`, the MCP tool's name).

Rejected: one map row per operation (37 rows that the registry already says).

Cheap to undo: one helper (`guards.py::_registered`) and one clause each in `coverage` and `_item_status`.
