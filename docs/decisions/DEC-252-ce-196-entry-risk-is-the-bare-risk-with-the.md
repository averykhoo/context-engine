---
type: Decision
id: DEC-252
title: 'CE-196: Entry.risk is the bare risk with the retired marker parsed off and Entry.head the heading as written, so G-W13 and re-close idempotency key on the risk, retired or not'
actor: claude-code/claude-opus-5-5
tasks: [CE-196]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:982d4f122a8bcb48db3d4735e51bc7d81a1c795ef7f216525949bb215ca28d49
---

A build-time call for CE-196, the agent's own, PROVISIONAL until the owner reviews it.

`review.py::entries` parses the `(retired <session>: <why>)` marker off the front of an entry's heading. `Entry.risk` is the bare risk, and the new `Entry.head` is the heading as written. G-W13 (`working.py::Engine.lint_review`) and a re-close's idempotency (`review.py::append`) both key on `review.py::key(source, risk)`. So they still match a residual from a task's `## Design review` once its entry is retired: G-W13 stays green, and a re-close files nothing new. If the marker stayed in `risk`, a retired reviewed residual would turn G-W13 red, and a re-close would file it again under a new id.
