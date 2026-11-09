---
type: Task
id: CE-218
title: 'Build ask decide: close a derivable owner question by an agent decision (US-24)'
pri: LATER
state: open
deps: [CE-217]
goals: [G-7]
source: session 2026-11-10a
created: 2026-11-10
moved: 2026-11-10a
updated: 2026-11-10a
---

Build `ask decide` (US-24, DEC-325): close an owner question as decided by an agent decision when US-24's triage step finds it derivable from the goals or earlier decisions.

- It mints a PROVISIONAL decision with the agent's actor, citing what it was derived from and fable's opinion, and closes the question with a pointer to that decision. It never writes `actor: owner`.
- FRAMEWORK §5.3 forbids this today (only the owner's answer closes a question, CE-20); amend §5.3 in place, and add a by-hand step to manual-mode.md (and its kit copy).
- The close digest flags every question closed this way, so the owner can overturn it.

## Read first

- US-24, DEC-325, CE-20
- working.py::Engine.ask_answer
