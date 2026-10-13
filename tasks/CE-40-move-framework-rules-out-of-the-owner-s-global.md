---
type: Task
id: CE-40
title: Move framework rules out of the owner's global CLAUDE.md
brief: "Audit each global rule: where it lives in the framework or move it; machine facts stay; trimming is the owner's call"
pri: LATER
state: open
deps: []
source: session 2026-10-13a
created: 2026-10-13
moved: 2026-10-13a
updated: 2026-10-13a
---

Owner, 2026-10-13a: framework rules belong in the framework, not the owner's global `~/.claude/CLAUDE.md`. That file mixes machine facts (two shells, broken bare `python`, conda paths, Docker in WSL, token recipes) with rules that are framework-shaped: the CI babysitter on every push, the fresh-user install trial after a release, the `.scratch/` sweep and its four classes, delegation and persistence, commit by path, gate before push, HANDOFF read and write-back, assurance traps.

Audit the global file section by section; for each rule, name where it already lives in FRAMEWORK, the kit contract or a runbook (quote the line), or move it there. Machine facts stay. Trimming the global file is the owner's call and the last step: propose the trimmed text, do not edit it unasked. Repos that have not adopted the framework still read the global file, so a rule moves out of it only once those repos are covered (CE-11) or the owner accepts the gap.
