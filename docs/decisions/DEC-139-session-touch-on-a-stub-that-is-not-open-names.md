---
type: Decision
id: DEC-139
title: session touch on a stub that is not open names a remedy per stub kind, not one --follows remedy
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:b30b1f5dc5611deaf3b38549720541d4f37a0154f40d325a88bdf85fff84bf65
---

The agent's call on CE-6, made while building `session touch` in session 2026-11-01b: what `session touch` tells a caller whose stub is not `kind: open`.

Options:
(a) one remedy for every stub kind, `session start --follows <key>`, as the plan said;
(b) a remedy per stub kind: a `close` stub gets `session start --follows <key>`; a `pause` stub gets `session start`, then `pause resume`; an `abandoned` stub gets `session start`, then do its baton.

Chose (b): (a) does not work for two of the three kinds, because working.py::Engine._followable refuses an abandoned or paused key, so the single remedy would send the caller into a second refusal.

Built in lane commit 1707e3b, on main as 29eb511; pinned by AC-172. Cheap to undo: the refusal text only.
