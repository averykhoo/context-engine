---
type: Decision
id: DEC-281
title: 'CE-126: G-W7 reds an op line whose `lane` value is malformed'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:487524ff37c426bdee1de05b797bd077262d42a741d9848442017ebe5f766e94
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: lint on the lane field.

G-W7 (`guards.py::tool_owned`) reds an op line that has a `lane` key whose value is not a string matching `store.py::LANE_RE`; an empty string counts as malformed, since the engine never writes one (no lane means no key). The engine only writes a checked lane, so a bad value is a hand edit or another tool's line; `commit.py::select` reads a non-string or empty lane as the coordinator's, so without the guard such a line would be filed silently. Like G-W7's parse check, it runs only where the repo has a board.

Cheap to undo: one Failure in one guard.
