---
type: Task
id: CE-212
title: task show splices the Log into every PLACEHOLDER in a record's body, not only the Log's
brief: Read path only; the files on disk are right
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

`task show` splices the Log into any `PLACEHOLDER` in a record's body, not only the Log's (found while picking up audio-workspace feedback, CE-193).

**What happened** (2026-11-08, session 2026-11-07e): `task show CE-193` printed its item 3, which cites `guards.py::ASK_PLACEHOLDER_RE`, with the Log entry spliced into the middle of that symbol name. The file on disk is right; only the read is wrong.

**At HEAD cb362ca:** working.py::Engine.show builds the shown Log as `okf.set_section(body, "Log", "PLACEHOLDER").replace("PLACEHOLDER", ...)`, and `str.replace` replaces every occurrence in the body. Any record whose text names `PLACEHOLDER` (ASK_PLACEHOLDER_RE, GATE_PLACEHOLDER and others are cited across the board) is shown corrupted, through the CLI and the MCP server alike.

**The fix:** set the Log section to its shown text directly (no sentinel), or use a sentinel that cannot occur in a body and replace it once. A test shows a record whose body names `PLACEHOLDER` above its Log and asserts the text comes back unchanged; sabotage it by restoring the `.replace` call.

## Traps

- An empty Log: the shown section must stay empty, as today (`if entries else ""`).
- The `head` cap and its note line ("showing N of M log entries") must still apply.

## Read first

- src/context_engine/working.py::Engine.show
- src/context_engine/okf.py::set_section

## Log
