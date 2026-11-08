---
type: Decision
id: DEC-280
title: "CE-126: an unparseable op line's lane is read from its text, and the line stays with that lane (CE-128 extended)"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:e2d6a87c0a9c1f89e849cf907ca6dd7372902f6a5426924211fca158cf4fd5ee
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: whose an unparseable op line is.

CE-128 reads the session of a line that does not parse from its text (`commit.py::session_of`). CE-126 extends it: `commit.py::lane_of` reads the lane the same way (`commit.py::LANE_FIELD`), so a line cut short stays with its own session and lane, and a reply names it `<key> lane <lane>`. A line naming no session still goes into whichever commit comes next, as CE-128 has it. This is why `lane` is written right after `session`: a line cut short keeps both.

Rejected: treating an unparseable line's lane as unknown (it would be filed as the coordinator's, the mis-filing CE-126 fixes).

Cheap to undo: one regex fallback.
