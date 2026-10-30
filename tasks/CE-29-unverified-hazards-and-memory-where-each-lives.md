---
type: Task
id: CE-29
title: 'Unverified hazards and memory: where each lives, how it is promoted (to an invariant or the contract) or pruned'
brief: 'Hazards are volatile, invariants durable: keep them apart (FRAMEWORK §2.1); memory is promoted or pruned, never a rule'
pri: LATER
state: open
deps: []
source: session 2026-10-12b
created: 2026-10-12
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-7]
---

Filed by CE-16 from the coverage map (docs/evidence/framework-coverage-2026-10-12.md): components 13 (unverified hazards) and 23 (memory), FRAMEWORK §2, §2.1, §6.7 and §7.4. Today hazards have no declared home (no route in context.toml, no record kind) and memory lives only in Claude Code's per-project auto-memory, outside the repo. Decide each one's home and route, and a housekeeping or close step that turns a confirmed hazard into a CE-23 register entry and a general memory lesson into a contract rule.

## Log

- 2026-10-15c (claude-code/claude-opus-5-5): dedupe-6 (2026-10-15c review): a hazard has 3-4 homes (the orientation note, "the board", task ## Traps, the register), and the spec never says which one a task-scoped hazard goes in. Recommendation (agent, given to the owner in chat; awaiting their word): a trap lives where its lifetime matches. (1) Known, and true only while one task is open: that task's ## Traps. (2) Suspected but unconfirmed ("do NOT fix blind"): a board row labelled hazard, which gives it an id, a tier, staleness and a close that resolves it into a register entry, a fix or a dismissal. (3) Confirmed and durable, outliving any task: a register INV-n (the task close already files residuals there). Drop the orientation note as a home: the banner is overwritten at every close. A trap in CLAUDE.md is a register entry or a runbook trap, plus a pointer.
- 2026-10-15e (claude-code/claude-opus-5-5): DEC-50 (owner, 2026-10-15e): the 2026-10-15c trap-home recommendation is accepted as given. A trap lives where its lifetime matches: task ## Traps, a hazard board row, or a register INV-n; never the banner. Writing it into FRAMEWORK stays under the CE-7 hold.
- 2026-10-30a (claude-code/claude-opus-5-5): rerank: Exit criterion 1 (coverage components 13 and 23): DEC-72 lifted the CE-7 freeze and DEC-50 rules the trap home, so the FRAMEWORK write-up is unblocked. The memory half stays the owner's.
