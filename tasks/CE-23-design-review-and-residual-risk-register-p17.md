---
type: Task
id: CE-23
title: 'Design review and residual-risk register (P17, P18): task section, promotion refusal above the threshold, register file, handover on deploy'
brief: US-14; FRAMEWORK 5.2 and 7.4; first real trial is CE-3 (a long-lived process); keep it light below the threshold
pri: NEXT
state: open
deps: []
source: session 2026-10-10b
created: 2026-10-10
moved: 2026-10-10b
updated: 2026-10-12b
review: [guard, write-op, shipped]
---

Design review and residual-risk register (P17, P18): task section, promotion refusal above the threshold, register file, handover on deploy.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-12b (claude-code/claude-opus-5-5): build: engine, tests, config, runbook, criteria landed in cc9195a (AC-26..29 tested, sabotage ALL RED in a temp copy). FRAMEWORK edits and the CE-3/CE-23 reviews + register seed next.

## Design review

affects: the session building or closing a reviewed task, the next session with no context, the owner, a human editing tasks with plain git, every repo the engine is pointed at
- eliminated: a re-close files a residual twice | rung: eliminate | control: the append is keyed on (task id, risk text), so a second close adds nothing (AC-27)
- reduced: a task above the threshold reaches NOW with no review | rung: reduce | control: the `task promote` refusal (AC-26)
- reduced: a review is broken by hand after promotion | rung: collective | control: G-W12 (AC-28)
- reduced: a closed task's residuals never reach the register | rung: reduce | control: `task close` files them under its lock (AC-27); G-W13 at rest
- reduced: the register is edited into a malformed state (a lost line, a reused INV id) | rung: collective | control: G-W13's entry checks; the file is tracked in git
- residual: a task that should carry `review` is left without it, so it gets no ceremony | rung: individual | why: the threshold is declared by the task's author; detecting the triggers from a diff is out of scope and would misfire on small edits | control: FRAMEWORK §5.2's threshold list and the runbook's `task set` note
- residual: a close refused after its register append leaves INV entries for a task that is still open | rung: reduce | why: the store's lock is not re-entrant and the register is not a record, so the two writes cannot be one atomic write | control: the append runs inside the close's check(), after the review is validated, and is idempotent, so the next close reuses the entries
- residual: a repo runs an older installed engine, so the register it is handed is stale | rung: individual | why: the handover is only as fresh as the installed engine (DEC-1: the engine is pointed at a repo, never vendored into it) | control: orient prints the engine version beside the count; reinstall the engine
F: the register grows by one entry per residual and changes only when the code holding an entry changes; whoever changes that code edits the entry, and G-W13 flags a missing or malformed one at every gate
A: the review is a plain body section and the register a plain markdown file, both read and fixed without the engine; the runbook does every step by hand (task promote, task close, register show)
M: one line format parsed by one function (review.parse), one template kept verbatim in the runbook and checked by a test, INV ids never reused
E: one new operation (`register show`) with one name across library, CLI and MCP; the register reuses the invariants home (§7.4) rather than a new record kind
