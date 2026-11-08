---
type: Decision
id: DEC-236
title: The standard and reserved prefix sets live once, in config.py::STANDARD_PREFIXES and config.py::RESERVED_PREFIXES
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:a7f4ad625c7216bd10284f5c36868915176c87129919375ea2eb6509b9c8193b
---

For CE-56: the standard prefixes (DEC-38) are read by init's refusals, lint G-D2, the kit's test and the register and criteria defaults.

The call: the standard and reserved prefix sets live once, in config.py::STANDARD_PREFIXES (role -> prefix: decision DEC, story STORY, criterion AC, question ASK, risk RISK, goal GOAL, baton BATON, pause PAUSE) and config.py::RESERVED_PREFIXES (EXP, HAZ, each with what it is reserved for). bootstrap.py, guards.py and the tests read them from there; review.py::PREFIX and criteria.py::PREFIX are pinned equal to them by a test.

Options:
(a) one home in config.py: chosen;
(b) a copy in each module: rejected, they drift.

Cost to undo: cheap.
