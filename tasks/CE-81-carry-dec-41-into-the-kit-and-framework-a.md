---
type: Task
id: CE-81
title: "Carry DEC-41 into the kit and FRAMEWORK: a target repo's engine env is pinned and lives in its folder"
brief: Kit README § 1, FRAMEWORK bootstrap step 2 and the upgrade procedure still say only 'its own env'; add the in-repo path
pri: NEXT
state: open
deps: []
source: session 2026-10-14d
created: 2026-10-14
moved: 2026-10-14d
updated: 2026-10-14g
---

DEC-41 (owner, 2026-10-14d) amends DEC-1: a target repo's engine env is a pinned, non-editable install kept inside that repo's folder and gitignored, never the repo's own env. The kit README § 1 (install and pin), FRAMEWORK.md's bootstrap step 2 ("installs the engine into its own environment") and its upgrade procedure still describe only a separate env. adhoc's trial set it up as `.context-engine/env/` (conda -p, python 3.12, pip install git+...@<sha>), with `.context-engine/` in .gitignore and the rebuild lines in adhoc's CLAUDE.md. Decide whether init should write the .gitignore line and the CLAUDE.md note.

## Traps

- A kit text change here does not reach adhoc until its pinned env is upgraded (that is the point of DEC-41); do not re-pin adhoc mid-trial without saying so.

## Read first

- DEC-1, DEC-41; `src/context_engine/kit/README.md` § 1 and § 4

## Log

- 2026-10-14g (claude-code/claude-opus-5-5): DEC-43 (owner, 2026-10-14g): start now; the CE-7 dep and the 2026-10-14c freeze are lifted for this task. adhoc keeps its pinned kit (DEC-41).
