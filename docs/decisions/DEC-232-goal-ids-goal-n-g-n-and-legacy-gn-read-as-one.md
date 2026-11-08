---
type: Decision
id: DEC-232
title: "Goal ids: GOAL-n, G-n and legacy Gn read as one goal by number; a new write must use the charter's spelling; no config key"
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:0ebe9bf303033c64c280279e0639cae452e5f5eeca60544180091843bc6ad905
---

For CE-56: DEC-38 makes GOAL the standard goal prefix, but the guards read only `G-n` (and the legacy `Gn`), and this repo's charter and every open task use `G-n` (DEC-162 keeps them).

The call: the guards read `GOAL-n`, `G-n` and the legacy `Gn` as one goal, by number (guards.py::GOAL_RE, guards.py::goal_number). A charter row is written `GOAL-n` or `G-n` (guards.py::CHARTER_FORM); two rows with one number are red. A stored record may name the goal in any of the three forms; a new write must use the charter's own spelling. No config key: the charter already says which form it uses.

Options:
(a) by number, the charter's spelling on new writes, no key: chosen;
(b) canonicalise every goal to GOAL-n: rejected, it reds every open task here, against DEC-162;
(c) accept either form on new writes: rejected, one repo then spells one goal two ways;
(d) a config key for the goal prefix: rejected, the charter already says it, and a default would flip adopted repos on upgrade.

Cost to undo: cheap (the goal regexes and their tests).
