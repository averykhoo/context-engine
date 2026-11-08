---
type: Decision
id: DEC-256
title: 'CE-196: G-W13 fails a register entry whose heading marker and `retired:` line disagree'
actor: claude-code/claude-opus-5-5
tasks: [CE-196]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:d5ba9930370b48d023d80c0ddb8a1e4d92e77efc0818456d84b5bdce9a3bf827
---

A build-time call for CE-196, the agent's own, PROVISIONAL until the owner reviews it.

G-W13 (`review.py::entry_problems`) fails a register entry whose heading says `(retired <session>: <why>)` but which has no `retired:` line. It also fails the converse, a `retired:` line under a heading with no marker. A retirement half done by hand would otherwise read as live in one view and as retired in the other. `retired` and `merged` stay out of `ENTRY_FIELDS`, which is G-W13's list of required fields, so a live entry does not need them.
