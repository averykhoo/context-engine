---
type: Decision
id: DEC-237
title: "A push made while no session was open is recorded by a `pushed:` receipt on a later session close (--pushed), not by a new op: orient stops flagging it once any close's receipt names a prefix of its commit hash (CE-176)"
actor: claude-code/claude-opus-5-5
tasks: [CE-176]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:e14a285a470de0019aa6d8016038e5050d82a37decf01e255a2494c112457e25
---

For CE-176: orient's Upstream part flags the upstream's newest push when no session window holds its time, and tells the agent to record it in this session's close, but nothing a close wrote was read back: only a later push inside a session cleared it.

The call: a push made while no session was open is recorded by a `pushed:` receipt on a later session close (`session close --pushed`), not by a new op. `working.py::Engine.upstream_lines` stops flagging the push once any `kind: close` entry's `pushed:` receipt names a prefix of its commit hash (`working.py::Engine._push_recorded_by`).

Options:
(a) a `pushed:` close receipt: chosen; the notice already points at the close, and the ledger entry is what the next session trusts;
(b) a new op (`push record <sha>`, a `push.ack` op line, or a stub field like `asked`): rejected, a new verb, MCP tool, manual-mode section and op name for one fact; its one gain, clearing mid-session, is moot when the session that sees the flag closes eagerly;
(c) clear on any later close (time only): rejected, it fails by passing: the close may say nothing about the push;
(d) clear when a close's summary or rows mention the hash: rejected, unvalidated, and it eats a digest line.

Not covered: a push inside a session that the session's close did not record.

Cost to undo: cheap.
