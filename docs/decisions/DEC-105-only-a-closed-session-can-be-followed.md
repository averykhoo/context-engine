---
type: Decision
id: DEC-105
title: Only a closed session can be followed
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:1ea06bb767c5ca2d96a3bad7ef50e377d954ac7d8b2dcade25a86f22019a1789
---

The agent's call on CE-84, made while building it in session 2026-10-30a: only a closed session can be followed.

Options:
(a) `session start --follows <key>` accepts only a `kind: close` ledger entry; open, paused and abandoned keys are refused, each remedy naming its own way back (work in it, `pause resume`, or do its baton);
(b) accept any ledger entry.

Chose (a): CE-84 links a follow-up to a closed session (DEC-45); a session that is not closed has its own way back, named in the refusal's remedy.

Built in lane commit f88f624, on main as 7920cbd (working.py::Engine._followable); pinned by AC-123. Cheap to undo.
