---
type: Decision
id: DEC-268
title: 'CE-178: task import invents nothing (no defaulted moved, updated, source or body) and runs no tier-cap, deps or goals check'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-178]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:6ad9e4310522279e3c1e16c32fad01327274b17e102e45b15c392662c919d712
---

A build-time call for CE-178, the agent's own, PROVISIONAL until the owner reviews it.

`task import` invents nothing: unlike `task new`, it adds no `moved`, `updated`, `source` or default body a record lacks. It runs no tier-cap, deps or charter-goals check at import; lint reports those on the result (G-W5, record references, G-I1), as it does after `decision import`.
