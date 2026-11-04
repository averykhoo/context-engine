---
type: Question
id: ASK-29
title: Merge zanzibar's ce-cutover into master and push it (no tag)?
brief: 'Recommend: after the design confirmations, fast-forward, gate on master, push, CI watcher; never a tag'
pri: NEXT
state: closed
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-04a
last_asked: 2026-11-04a
blocks: [CE-167]
status: deprecated
closed: 2026-11-04a
answered: {on: 2026-11-04, session: 2026-11-04a, decision: DEC-151}
---

## Context

CE-167's cutover is built and verified on zanzibar's local branch `ce-cutover` (head 3e63fd7, 7 commits on
master 4826a01; worktree C:/Users/user/PycharmProjects/zanzibar-ce-cutover). Zanzibar's full ten-phase gate
is green on 3e63fd7, the engine lint is clean, and an independent verifier passed 8/8
(docs/evidence/ce167-zanzibar-cutover-2026-11-03.md). The merge would be a fast-forward. Pushing master also
sends the two unpushed 0.1.2 records commits (origin/master is b743587), and gate.yml and docs.yml run on
every master push. A v* tag would publish to PyPI, so no tag is proposed. After the merge, the main checkout
needs its own engine env and SessionStart hook (the import script's bootstrap step).

## Options

- Fast-forward master to 3e63fd7 now, re-run the gate on master, push, and watch CI; no tag.
- Merge locally now and push later.
- Hold the merge until the design confirmations (the companion question) are answered.

## Recommendation

Answer the design confirmations first, then the first option: everything on the branch is checked, and a
fast-forward plus CI watcher is the same shape CE-11 took.

## Log

- 2026-11-04a (claude-code/claude-opus-5-5): answered by the owner: DEC-151
