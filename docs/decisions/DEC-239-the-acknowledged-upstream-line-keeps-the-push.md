---
type: Decision
id: DEC-239
title: "The acknowledged Upstream line keeps the push state and names the close that recorded it: `- the last push to <up>: <sha>, at <t> (while no session was open; recorded in <key>'s close)` (CE-176)"
actor: claude-code/claude-opus-5-5
tasks: [CE-176]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:b0238a971e7659aeb8b887ed73d7be3f7dc29e1b46c229bb8fc5c62c8aa39001
---

For CE-176: once a close records a push made while no session was open, orient's Upstream part must still give the push state (CE-195: the banner no longer carries it), and should say where it was recorded.

The call: the acknowledged Upstream line keeps the push state and names the close that recorded it: `- the last push to <up>: <sha>, at <t> (while no session was open; recorded in <key>'s close)`, where `<key>` is the newest close whose `pushed:` receipt names it. The unrecorded line keeps its text through "tell the owner" and gives its remedy as the command: `session close ... --pushed "<sha>: <what was pushed, and whether the gate ran first>"`.

Options:
(a) keep the push state and name the close: chosen;
(b) drop the line once recorded: rejected, the push state would then be said nowhere;
(c) the in-session form, unmarked: rejected, it would hide that the push came outside a session.

Cost to undo: cheap.
