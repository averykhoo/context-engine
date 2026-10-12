---
type: Task
id: CE-28
title: Cross-repo owner-question index generated at session start (FRAMEWORK §5.6)
brief: Generated and disposable, outside the repos; each repo's board stays the source of truth
pri: SOMEDAY
state: open
deps: [CE-15]
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-12b
updated: 2026-10-12b
---

Filed by CE-16 from the coverage map (docs/evidence/framework-coverage-2026-10-12.md): ritual §5.6 (the owner digest). The digest itself is built: session close refuses a summary outside 1 to 7 lines (working.py::Engine.session_close) and writes it into the ledger. Not built: the generated cross-repo index (e.g. ~/.claude/owner-questions.md with last_asked) and the one-line start-of-session nag about other repos' overdue questions. Only useful once a second repo runs the framework, hence the dep on CE-15. The answer-in-place file is CE-19.
