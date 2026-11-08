---
type: Decision
id: DEC-269
title: 'CE-178: task import has no --dry-run and is not a commit milestone, as decision import is not'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-178]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:6736279eb7c603bab984246da7c8e30c435251ead629a3682a57937349e4196f
---

A build-time call for CE-178, the agent's own, PROVISIONAL until the owner reviews it.

`task import` has no `--dry-run`: `Store.create_many` checks every record before it writes a byte, so a refused import writes nothing (cheap to add later). An import is not a commit milestone, as `decision import` is not: the session commits it by path.
