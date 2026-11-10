---
type: Task
id: CE-221
title: 'Ship the rule: never message a running workflow agent; hand it input by file'
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-10b
created: 2026-11-10
moved: 2026-11-10b
updated: 2026-11-10b
---

Ship the rule: never message a running workflow agent (adhoc's layer-2 note, 2026-11-10; audit item 3). In adhoc, messaging one created duplicates.

- To give a running workflow agent input, write it to a scratch file the agent's prompt told it to read, or let the agent finish and pass the input to the next run.

Changes: kit/docs/runbooks/fan-out.md § Workflows (the docs/runbooks copy stays byte-equal, LF).
