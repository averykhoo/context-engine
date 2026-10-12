---
type: Task
id: CE-20
title: Engine refuses task close on an ASK-n; questions close only through ask answer
brief: 'FRAMEWORK §5.3: closed only by an owner answer; remedy names ask answer. Sabotage the refusal'
pri: NEXT
state: closed
deps: []
source: session 2026-10-09f
created: 2026-10-09
moved: 2026-10-12c
updated: 2026-10-12c
status: deprecated
closed: 2026-10-12c
---

Found by the 2026-10-09 FRAMEWORK consistency audit (finding A20): working.py accepts task close ASK-n today. FRAMEWORK §5.3 now notes the gap.

## Log

- 2026-10-12c (claude-code/claude-opus-5-5): closed: Engine.close refuses an ASK-n with a remedy naming ask answer / ask later; runbook § task close and FRAMEWORK §5.3 updated; test sabotaged red
