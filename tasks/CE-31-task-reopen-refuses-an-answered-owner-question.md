---
type: Task
id: CE-31
title: task reopen refuses an answered owner question
brief: 'An answered ASK never reopens: its answer is a decision; revise that decision or ask a new question'
pri: LATER
state: open
deps: []
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-12d
updated: 2026-10-12d
---

Found during CE-20 (BTN-2, decided 2026-10-12d). `working.py::Engine.reopen` accepts an `ASK-n` and leaves `answered:` behind, so an open question claims an answer (the CE-20 asymmetry: `Engine.close` refuses a question, reopen does not).

Decision: refuse, do not clear `answered:`.
- Clearing it would orphan the decision whose `answers: ASK-n` still points at the question, and a later `ask answer` would make a second decision answer the same question.
- The owner's answer is a decision: changing it is a decision amend/correct/supersede (CE-5); a follow-up is a new `ask new` citing ASK-n and its DEC.

Scope:
- `Engine.reopen` refuses an id of the question kind that carries `answered:`, with a remedy naming `record amend <DEC>` (supersede once CE-5 lands) and `ask new`.
- A question closed WITHOUT `answered:` (a pre-CE-20 `task close`, audit A20) may still be reopened: that is the repair path.
- Runbook § task reopen gets the same rule and its why; FRAMEWORK §5.3 one line.
- Optional lint: an open question carrying `answered:` is red.
- Sabotage the refusal (fresh PYTHONPYCACHEPREFIX). Check whether the change crosses the review threshold (`write-op`).

## Read first
- working.py::Engine.close (the CE-20 refusal, commit f0064ff)
- working.py::Engine.reopen
- working.py::Engine.ask_answer
- docs/runbooks/manual-mode.md § context-engine task reopen
