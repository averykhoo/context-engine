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
updated: 2026-10-15c
---

This repo adopted the CE-38 kit block on 2026-10-13b (owner: dogfood the whole framework while building it). CLAUDE.md still restates what docs/framework/contract.md carries: session start, several-tasks delegation, fable, commit by path, op-owned fields, never renumber. Keep in CLAUDE.md only what is this repo's (interpreter path, gate, sabotage rule, spike/, FRAMEWORK upkeep) and what narrows the contract. CLAUDE.md is owner-loaded: show the owner the diff before committing. Pairs with CE-40 (the same move out of the global CLAUDE.md).

## Log

- 2026-10-14a (claude-code/claude-opus-5-5): Audit 2026-10-14a: CLAUDE.md sat at its G-D1 line cap. CE-69 removes the lines that contradicted the contract (session start, commit, Closes:), and the rest of the trim stays here.
- 2026-10-15c (claude-code/claude-opus-5-5): Owner, 2026-10-15c, verbatim: "dedupe-3, 4, 5, and 7 seem related, some of this is because the framework itself must contain the rules to inject into a new repo's claude, the rest is probably an accident and can be cleaned up eventually". The findings (2026-10-15c redundancy review). dedupe-3: the HANDOFF banner restates durable CLAUDE.md rules (fable, ask before push, close eagerly, CRLF merge, linux_gate). dedupe-5: "close eagerly" has about 7 homes (FRAMEWORK §6.3, the contract, procedures.md, the plugin skill, CLAUDE.md, the banner, memory); the kit copies, AC-33 and the skill quotes are byte-checked, and the CLAUDE.md, banner and memory copies are not. dedupe-7: the CLAUDE.md § Sabotage rule restates sabotage.md § Traps' bytecode-cache trap; replace it with a pointer. Keep the copies the kit must inject (checked); cut the unchecked ones. Idea: a lint that flags a sentence of 8 or more words in two routed files unless one is a declared, checked copy. dedupe-4 is on CE-40.
