---
type: Task
id: CE-47
title: Trim this repo's CLAUDE.md to repo-only rules now that it imports the contract
brief: Rules the imported contract carries are duplicated in CLAUDE.md and will drift
pri: LATER
state: open
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-14a
---

This repo adopted the CE-38 kit block on 2026-10-13b (owner: dogfood the whole framework while building it). CLAUDE.md still restates what docs/framework/contract.md carries: session start, several-tasks delegation, fable, commit by path, op-owned fields, never renumber. Keep in CLAUDE.md only what is this repo's (interpreter path, gate, sabotage rule, spike/, FRAMEWORK upkeep) and what narrows the contract. CLAUDE.md is owner-loaded: show the owner the diff before committing. Pairs with CE-40 (the same move out of the global CLAUDE.md).

## Log

- 2026-10-14a (claude-code/claude-opus-5-5): Audit 2026-10-14a: CLAUDE.md sat at its G-D1 line cap. CE-69 removes the lines that contradicted the contract (session start, commit, Closes:), and the rest of the trim stays here.
