---
type: Task
id: CE-243
title: Open owner questions are listed twice in orient and share NEXT's cap with work
brief: states the problem; decide the design first, none is pre-decided
pri: LATER
state: open
deps: []
goals: [G-1]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

Open owner questions are listed twice in orient and share NEXT's cap with work.

adhoc-microphone-array (AD-112 item 16): "NEXT already holds 5 of 5", with questions among the five. `ask new --pri` defaults to NEXT (cli.py), and working.py::Engine._cap_check counts every open board item of a tier, questions included, while orient already lists open questions in their own section. So a question takes a work slot and appears twice. docs/evidence/engine-feedback-2026-11-17.md, F16.

This task states the problem only; the design is open (DEC-100, answered questions skip the cap, is the one filed precedent). Decide it first: a PROVISIONAL call if cheap to undo, otherwise an ASK.

## Traps

- No design is pre-decided here (fable's second opinion, evidence doc § Second opinion item 7): exempting asks from the cap is one option, not the task.
- Questions must stay visible: whatever changes, orient still shows every open question once.

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F16, § Second opinion item 7
- working.py::Engine._cap_check, working.py::Engine._pending_asks; DEC-100

## Log
