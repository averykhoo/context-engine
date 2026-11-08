---
type: Decision
id: DEC-321
title: CE-40 closes once its doc is committed and verified (doc freeze, then task close), with the owner's paste of section 4 as a Still owed line
tasks: [CE-40]
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:d6d5bce92a303a2d5a7e3bcb45f96de0225e697f56c217f07e1ff8ee674dc1e3
---

An agent's call under P8 (cheap to undo: a task can be reopened), made by CE-40's builder in session 2026-11-07e on 2026-11-08, following the planner's design. Not owner words.

CE-40 closes once its doc is committed and verified by an agent other than its builder: `context-engine doc freeze` on the doc first, then `context-engine task close CE-40` (FRAMEWORK §6.7: the close refuses while the doc is still ACTIVE-PLAN). The owner's paste of the doc's section 4 into `~/.claude/CLAUDE.md` is carried as a "Still owed" line in the session close (DEC-162), rather than CE-40 staying open on the board until the paste. The paste is outside the repo and the owner's; a board row waiting on it would sit open with nothing for an agent to do.
