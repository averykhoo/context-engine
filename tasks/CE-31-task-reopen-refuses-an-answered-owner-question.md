---
type: Task
id: CE-31
title: task reopen refuses an answered owner question
brief: 'An answered ASK never reopens: its answer is a decision; revise that decision or ask a new question'
pri: NEXT
state: open
deps: []
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13a
review: [guard, shipped]
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

## Design review

affects: the owner, whose answer (a stamped decision) an open question would contradict; the next session, which reads an open question as unanswered and may raise or re-answer it; a plain-git human reopening by hand from manual-mode.md; every deployed repo, which gets the engine refusal and the kit runbook copy
- eliminated: a reopen clears `answered:`, orphaning the decision whose `answers:` names the question, and a later `ask answer` makes a second decision answer it (the design refuses and never clears; `answered` joins the operation-owned keys, so `task set` cannot clear it either)
- reduced: `task reopen ASK-n` on an answered question leaves an open question that claims an answer | rung: reduce | control: Engine.reopen refuses a question carrying `answered:`, naming `record amend <DEC>`, `decision supersede <DEC> <new>` and `ask new`; sabotaged
- reduced: a by-hand reopen (manual mode, or a raw edit) leaves `answered:` on an open question | rung: reduce | control: G-W4 reds an open question that carries `answered:`, naming the same remedies; sabotaged
- reduced: the refusal blocks the repair of a question closed without an answer (a pre-CE-20 `task close`, audit A20) | rung: reduce | control: the refusal keys on `answered:`, not on the kind; a test reopens an unanswered closed question
- residual: a raw edit that reopens a question and also deletes `answered:` passes lint, leaving a decision whose `answers:` names an open question | rung: collective | why: telling a deliberate repair from a mistake needs the decision's history, and no guard yet joins decisions' `answers:` to the board | control: manual-mode.md § task reopen and § task set say an answer changes only through its decision; the raw edit shows in the commit diff
F: goes stale if the question kind stops using `answered:` or the decision ops change name (the remedy text and runbook name `record amend`, `decision supersede`, `ask new`); a test pins each
A: by hand, manual-mode.md § task reopen says to stop on a question with `answered:`; lint G-W4 reports it at rest; reading is one frontmatter key
M: one refusal in Engine.reopen and one clause in G-W4 sharing the same remedy wording; `answered` in BOARD_OWNED beside `last_asked`
E: mirrors CE-20's refusal in Engine.close; reuses G-W4, Refusal and the BOARD_OWNED table; one runbook paragraph in § task reopen and one line in FRAMEWORK §5.3

## Log

- 2026-10-13a (claude-code/claude-opus-5-5): Built (2026-10-13a): Engine.reopen refuses a question carrying answered: (remedy: record amend / decision supersede / ask new); answered joins BOARD_OWNED so task set cannot clear it; G-W4 reds an open question carrying answered:; a question closed without answered: still reopens. Runbook § task reopen, § task set, § lint G-W4 and FRAMEWORK §5.3/§8 updated. Above the threshold as [guard, shipped]; design review written before building. Awaiting review; not closed.
