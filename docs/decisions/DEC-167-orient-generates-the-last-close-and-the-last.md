---
type: Decision
id: DEC-167
title: orient generates the last close and the last push; no review queue until CE-187 (CE-195)
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
refs: [DEC-163, US-21]
decided: 2026-11-06
session: 2026-11-06f
body_sha: sha256:d5034b06384f93e6e3a60fa0e3f26fa1172a2c6cd8d6a60eb9c0dcaf7594753a
---

The agent's call on CE-195 (DEC-163, US-21), made while building it in session 2026-11-06f: what orient generates so the banner need not carry it.

Options:
(a) a `Last close <key>: what it closed with` part (rank 2, above the banner in the cap's order): the newest close's rows, digest and still-owed lines, with its thread when it continued one, left out when this session's own `follows`/`continues` part already shows that close; and the `Upstream` part names the last push's commit and time when it came inside a session (it already named the time of one made outside every session). The "review queue" is not generated: no record defines it today; CE-187's accept list is where agent calls awaiting the owner will be read from;
(b) the same, and also a count of PROVISIONAL agent decisions as a review queue now.

Chose (a): each part is read from a record (the ledger, git's reflog), so it cannot go stale the way a banner line does; (b) would invent a queue CE-187 is about to define. What is not derivable (a CI run's verdict, a lesson) stays hand-written: in the close digest, which orient now shows, or in a durable banner line.

Built in working.py::Engine.orient and working.py::Engine.upstream_lines; pinned by AC-185 and AC-93. Cheap to undo.
