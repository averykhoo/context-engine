---
type: Decision
id: DEC-276
title: "CE-126: every lane is taken by the session close, the session pause AND the pause record (DEC-84 named only the close; a pause ends the session's work the same way)"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:53fbf12b7d50e980949b33f0806a64c3b6704587737a0832f2d71ef47fcd3d2d
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: which commits take every lane of the session.

DEC-84 says "close takes all lanes". The build has three operations take every lane of their own session (`commit.EVERY_LANE`): the session close (`working.py::Engine.session_close`), the session pause (`working.py::Engine.session_pause`) and the pause record (`working.py::Engine.pause_open`). A pause ends the session's work the same way a close does: what a dead or finished subagent left uncommitted under the key must reach HEAD with it, or the pause's own list of uncommitted paths would name files its commit could have carried (INV-45). None of them ever takes another session's lines: the per-session split of CE-125 stays.

Rejected: only the close (a paused session would leave its subagents' lines in the tree, and the pause record would list them as uncommitted).

Cheap to undo: one flag set in two methods, one argument in a third.
