---
type: Task
id: CE-110
title: 'Owner global CLAUDE.md: never bash a variable path, never background an && chain, set ulimit -u 200'
brief: Owner/coordinator to add three shell rules to ~/.claude/CLAUDE.md; agents must not edit it
pri: SOMEDAY
state: closed
deps: []
goals: [G-7]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-11-14a
updated: 2026-11-14a
status: deprecated
closed: 2026-11-14a
---

Owner global CLAUDE.md: never bash a variable path, never background an && chain, set ulimit -u 200

What went wrong (adhoc AAR entry 13 and 20, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: A subagent ran a non-script file through bash from a shell-variable slip (entry 13), and the laptop ran out of commit memory from backgrounded chains (entries 19-21); the rule had no tracked home (entry 20). Text to add to the owner's global ~/.claude/CLAUDE.md: (1) never `bash "$var"` a path; (2) never background an `&&` chain, use run_in_background on one script; (3) `ulimit -u 200` in the shell before spawning. Engine agents may not edit that file, so the owner or coordinator applies it; close when done. Census F8: NEW, owner preference. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F8).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): rerank: Serves no G-n (an owner preference for ~/.claude/CLAUDE.md, outside the repo). The drop is not applied; it is an owner question.
- 2026-10-31a (claude-code/claude-opus-5-5): DEC-131: rule 3 out (ulimit -u errors in Git Bash, docs/evidence/ulimit-gitbash-2026-11-01.md); waiting on the owner to paste rules 1 and 2 (draft text in session 2026-10-31a's chat), then close
- 2026-11-14a (claude-code/claude-opus-5-5): closed: Rules 1 and 2 (DEC-131's wording) appended to the owner's ~/.claude/CLAUDE.md § Assurance traps by the coordinator at the owner's request (DEC-343 item 5: "help me add that"); rule 3 stays out (DEC-131).
  residual risk: none
