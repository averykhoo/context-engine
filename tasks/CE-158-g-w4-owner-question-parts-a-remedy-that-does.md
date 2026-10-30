---
type: Task
id: CE-158
title: 'G-W4 owner-question parts: a remedy that does not clear, and options misread'
brief: CE-44 verifier residuals (3371106), all in guards.py::ask_parts
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

G-W4 owner-question parts: a remedy that does not clear, and options misread.

Source: CE-44's close (3371106), three verifier residuals, all in how guards.py::ask_parts reads a question.
- G-W4's remedy `task section <id> <part> "<text>"` does not clear the failure when the part is missing: okf.py::set_section appends the new `## <part>` after `## Log`, and ask_parts stops at `## Log`; the test asserts only that the remedy names `task section`.
- guards.py::ASK_OPTION_RE allows 0-3 leading spaces, so one option with an indented sub-bullet passes as two options.
- Options written as bold labels (`**A:** ...`) end the Options part and count as none, and a prose line starting with a plain label (`Log:`, `Question:`) splits the body.

## Traps

- none yet

## Read first

- guards.py::ask_parts
- okf.py::set_section

## Log
