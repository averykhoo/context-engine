---
type: Task
id: CE-35
title: "Decision relink: move a decision's code link when the code moves"
brief: 'logged like link, re-checks existence; code: is never hand-edited'
pri: NEXT
state: open
deps: []
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13a
---

Filed by CE-14-fix (session 2026-10-12d). G-T3 (src/context_engine/guards.py::decision_code) fails a current decision whose `code:` link no longer resolves. `decision link` only adds; no operation removes or replaces a link, and `code` is written by an operation, so it is not hand-edited: today the only remedy is restoring the code. Add one (e.g. `decision link --replace <old>`), its runbook section, and point the G-T3 remedy and INV-15 at it.
