---
type: Question
id: ASK-23
title: Retire CE-145, folding its agent-half observation into INV-31?
brief: CE-145 has nothing to build here; INV-31 already tracks the wait
pri: LATER
state: open
deps: []
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
last_asked:
blocks: [CE-145]
---

## Context

CE-145 (INV-31 agent half) has nothing to build in this repo: it waits for a natural compaction in adhoc, which INV-31's register row already tracks (docs/evidence/inv31-adhoc-probe-2026-10-23.md). The 2026-10-30a rerank moved it to SOMEDAY and proposes retiring it; the retirement is not applied.

## Options

- Fold the agent-half observation into INV-31 and retire CE-145.
- Keep CE-145 at SOMEDAY as a separate task.

## Recommendation

Fold the agent-half observation into INV-31 and retire CE-145: the register row already tracks the same wait, and a second open task for it duplicates the tracking.
