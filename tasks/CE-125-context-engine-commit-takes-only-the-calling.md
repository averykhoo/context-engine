---
type: Task
id: CE-125
title: context-engine commit takes only the calling session's op lines
brief: Never sweep another session's op lines into a commit silently; name what is left behind
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-21b
updated: 2026-10-21b
---

context-engine commit takes only the calling session's op lines

`context-engine commit` takes every uncommitted op line, so a dead or concurrent session's lines ride into the next session's commit. Seen in adhoc: a dead session's op lines were swept into `a24d18d` (adhoc AAR entry 22, docs/evidence/adhoc-feedback-2026-10-21.md; scored in docs/evidence/adhoc-trial-score-2026-10-21.md). CE-45 chose the sweep on purpose; this revisits it: default to the calling session's lines, and name the lines left behind (whose, how many) in the commit's output. CE-101 (foreign commits in orient) is related, not the same.

## Traps

## Read first
- docs/evidence/adhoc-feedback-2026-10-21.md (entry 22)

## Log
