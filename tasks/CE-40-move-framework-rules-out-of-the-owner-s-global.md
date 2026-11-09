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
moved: 2026-11-07e
updated: 2026-11-10a
goals: [G-6, G-7]
---

Owner, 2026-10-13a: framework rules belong in the framework, not the owner's global `~/.claude/CLAUDE.md`. That file mixes machine facts (two shells, broken bare `python`, conda paths, Docker in WSL, token recipes) with rules that are framework-shaped: the CI babysitter on every push, the fresh-user install trial after a release, the `.scratch/` sweep and its four classes, delegation and persistence, commit by path, gate before push, HANDOFF read and write-back, assurance traps.

Audit the global file section by section; for each rule, name where it already lives in FRAMEWORK, the kit contract or a runbook (quote the line), or move it there. Machine facts stay. Trimming the global file is the owner's call and the last step: propose the trimmed text, do not edit it unasked. Repos that have not adopted the framework still read the global file, so a rule moves out of it only once those repos are covered (CE-11) or the owner accepts the gap.

## Log

- 2026-10-15c (claude-code/claude-opus-5-5): dedupe-4 (2026-10-15c review; owner words on CE-47): the global CLAUDE.md and FRAMEWORK state delegation, persistence, the CI watcher, .scratch and sabotage twice, worded differently, and they have already diverged. The global file says subagents default to opus; FRAMEWORK §6.6 says "the cheaper model that can do it" (DEC-45, CE-83 pending). Suggestion: the global file keeps machine facts plus rules for repos without the framework, and points at the framework for method in framework repos.
- 2026-11-06c (claude-code/claude-opus-5-5): DEC-162: the owner accepts the gap (no wait on CE-11). An agent drafts the trimmed global CLAUDE.md text to a tracked doc, and the owner pastes it.
- 2026-11-07e (claude-code/claude-haiku-5-5): Done: audit of the global CLAUDE.md against the framework, with the Workflow agent() model-inheritance harness fact fix (commit 2efe546, independently verified). Left for the owner: trimming the global CLAUDE.md (owner's call, DEC-162) by pasting the proposed trimmed text; CE-40 stays open until then.
- 2026-11-10a (claude-code/claude-opus-5-5): 5cf44d0: CE-40: audit the global CLAUDE.md against the framework; propose the trimmed text
