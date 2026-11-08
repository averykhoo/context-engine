---
type: Decision
id: DEC-231
title: Lint G-D2 reds a task prefix equal to a standard (DEC, STORY, AC, ASK, RISK, GOAL, BATON, PAUSE) or reserved (EXP, HAZ) one; other kinds' prefixes are not checked
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:13f3838e43f35ead819f063ee84f5c0d327c424faf5a2e9f132b7f797ffdb0e4
---

For CE-56: DEC-38 reserves EXP and HAZ and gives tasks a prefix of their own; nothing caught a task prefix that reads as another kind's ids.

The call: lint G-D2 (guards.py::ids) reds `context.toml` when the `[working] task` kind's prefix is a standard one (DEC, STORY, AC, ASK, RISK, GOAL, BATON, PAUSE) or a reserved one (EXP, HAZ). The remedy is to rename the tasks by hand, each keeping its number, with its old id in `aliases` (FRAMEWORK §11.4). Other kinds' prefixes are not checked, and neither is prefix length.

Options:
(a) the task kind only, in lint: chosen;
(b) every kind against the roles' prefixes: rejected, a repo's kinds need not carry the kit's names, so matching role by kind name gives false reds;
(c) refuse at config load: rejected, it bricks every command over a convention, where a lint failure reds the gate and is fixable.

Cost to undo: cheap (one block in G-D2 and its test).
