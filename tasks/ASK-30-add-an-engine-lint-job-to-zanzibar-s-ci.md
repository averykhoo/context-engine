---
type: Question
id: ASK-30
title: Add an engine lint job to zanzibar's CI?
brief: 'Recommend: yes, as its own change after the merge'
pri: LATER
state: closed
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-04a
last_asked: 2026-11-04a
status: deprecated
closed: 2026-11-04a
answered: {on: 2026-11-04, session: 2026-11-04a, decision: DEC-152}
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

## Log

- 2026-11-04a (claude-code/claude-opus-5-5): answered by the owner: DEC-152
