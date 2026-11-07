---
type: Task
id: CE-158
title: 'G-W4 owner-question parts: a remedy that does not clear, and options misread'
brief: CE-44 verifier residuals (3371106), all in guards.py::ask_parts
pri: NOW
state: closed
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-07d
updated: 2026-11-07d
status: deprecated
closed: 2026-11-07d
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
- working.py::Engine.doc_archive (CE-153's refusal, DEC-162)

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): Promoted LATER->NEXT (DEC-162): a refusal whose printed remedy does not clear it is a trap, and the contract tells agents to follow remedies.
- 2026-11-06c (claude-code/claude-opus-5-5): Takes CE-153's one-line refusal (DEC-162: 'CE-153 | merge into CE-154, do now'; ranked point 3: 'Promote CE-156 and CE-158, and take CE-153's one-line refusal with them'): working.py::Engine.doc_archive refuses the engine's own control files, context.toml and the op log (docs/ledger/ops.jsonl), which CE-96 made archivable when it dropped the non-.md refusal (654ea03, verifier finding 1). Carried here at NEXT, not in CE-154 at LATER, so the 'do now' holds while NOW holds CE-187 and NEXT is at its cap of five; agent's call, PROVISIONAL.
- 2026-11-07d (claude-code/claude-opus-5-5): closed: built and verified (independent PASS, round 2): G-W4's remedy clears, question parts and options read as written, doc archive refuses the control files
  residual risk: INV-106, INV-107
