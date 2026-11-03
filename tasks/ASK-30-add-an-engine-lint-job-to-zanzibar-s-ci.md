---
type: Question
id: ASK-30
title: Add an engine lint job to zanzibar's CI?
brief: 'Recommend: yes, as its own change after the merge'
pri: LATER
state: open
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-03b
last_asked: 2026-11-03b
---

## Context

After CE-167, zanzibar's records are checked by `context-engine lint`, but zanzibar's CI (gate.yml) does not
install the engine or run it, so record lint is a local-only gate step there. Adding it is a CI config change
in zanzibar.

## Options

- Add an engine-install-and-lint job to zanzibar's gate.yml (pinned to the engine ref), as a follow-up after
  the merge.
- Keep lint local only.

## Recommendation

The first, as its own change after the merge: a red record stays invisible to CI otherwise.
