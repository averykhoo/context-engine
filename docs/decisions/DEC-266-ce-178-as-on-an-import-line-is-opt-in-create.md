---
type: Decision
id: DEC-266
title: 'CE-178: as on an import line is opt-in (create_many keep_history), so task new --id and decision import cannot launder a chosen moved'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-178]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:a2d05292965cc31d5f68948de6787b51a5a94c2c9d37d56940f0bf7984acb76e
---

A build-time call for CE-178, the agent's own, PROVISIONAL until the owner reviews it.

`as` on an import's op line is opt-in: `Store.create_many(keep_history=True)` writes it, and only `task import` sets it. `task new --id` and `decision import` log no `as`, so a `moved` value a caller chooses cannot be laundered past G-W7 through them.
