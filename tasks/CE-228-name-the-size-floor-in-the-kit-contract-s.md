---
type: Task
id: CE-228
title: Name the size floor in the kit contract's coordinator rule at the next contract version bump (CE-219)
brief: 'Wait for a version bump: changing it now turns G-D0 red in every adopting repo'
pri: LATER
state: open
deps: []
goals: [G-3, G-7]
source: session 2026-11-11a
created: 2026-11-11
moved: 2026-11-11a
updated: 2026-11-12a
---

Name the size floor in the kit contract's coordinator rule at the next contract version bump (CE-219).

CE-219 put the size floor and the build ladder in FRAMEWORK §6.6 and P11, and named the floor there as the coordinator rule's one exception. The contract's coordinator bullet still reads "each task, even a lone one, goes to its own subagent through ultracode", and FRAMEWORK §6.6's coordinator paragraph carries the same bytes (AC-33). Changing `src/context_engine/kit/contract.md` now, without a version bump, turns G-D0 red in every adopting repo (DEC-310), so the line waits; meanwhile this repo's CLAUDE.md narrows the contract.

At the next contract version bump, change the coordinator bullet in FRAMEWORK §6.6, `src/context_engine/kit/contract.md` and `docs/framework/contract.md` together (byte-equal, AC-33 and G-D0). Suggested bullet:

```
- each task, even a lone one, goes to its own subagent through ultracode, unless its edits are
  under the size floor (§6.6); that agent owns the task end to end, can persist (not `Explore`),
  and pushes the work down again, to its own subagents or a workflow;
```

Then FRAMEWORK §6.6's sentence that a repo takes the floor up in its own contract can go, and the test claiming the ladder's criterion (tests/test_roster.py) can assert the bullet. Do it with CE-207, at the same bump.

## Traps

- Not before a contract version bump: G-D0 compares an adopting repo's contract with the installed kit's.
- FRAMEWORK §6.6's coordinator paragraph and the kit contract change in the same commit, or AC-33 goes red.

## Read first

- docs/framework/FRAMEWORK.md (§6.6, the size floor and the build ladder)
- src/context_engine/kit/contract.md (§ Rules, the coordinator)

## Log

- 2026-11-12a (claude-code/claude-opus-5-5): fable design review (2026-11-12, docs/evidence/fable-review-dec-328-336-2026-11-12.md note 2): measured 2026-11-12, CLAUDE.md is at 140/140 lines and 9996/10000 bytes and fan-out.md at 7990/8000 bytes; the next edit to either is a red G-D1, so plan the cap raise with this bump (and CE-207).
