---
type: Question
id: ASK-25
title: Merge intervals ce-cutover into master and push?
brief: Recommend merge now; push only after prepush, with a CI watcher
pri: NEXT
state: open
deps: []
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-02a
updated: 2026-11-02a
last_asked: 2026-11-02a
blocks: [CE-11]
---

## Context

CE-11's cutover is done on a local branch: intervals `ce-cutover` (head 8f1cbab, worktree
C:/Users/user/PycharmProjects/intervals-ce-cutover), 7 commits on master fa4cf12. Rehearsed twice on
clones, then verified independently on 2026-11-02 (10/10 checks pass: refs, bundle backup, full gate
re-run itf 27798 + rest 7188 passed, lint clean, conservation 87/87 with 0 lost and 0 extra, HANDOFF
22/22 items on the board, CLAUDE.md rules intact, engine pin 309641b on origin/main). intervals master
is untouched, and was already 4 docs-only commits ahead of origin/master before the cutover.
Backup: C:/Users/user/intervals-backup-2026-11-02/intervals.bundle (verified).

## Options

- Merge `ce-cutover` into intervals master now (fast-forward), give the main checkout its own engine
  env and SessionStart hook, re-run the gate there, then push after `tools/prepush.sh` with a CI watcher.
- Merge into local master now, but hold the push.
- Hold the merge; leave the branch and worktree as they are.

## Recommendation

Merge now and push after prepush: the branch is verified, is a fast-forward, and every later
intervals session otherwise runs on a stale master. The push stays yours to approve.
