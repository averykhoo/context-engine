---
type: Task
id: CE-235
title: List the README under reader_docs in each adopted repo (DEC-340)
pri: NEXT
state: open
deps: []
goals: [G-6]
source: session 2026-11-13a
created: 2026-11-13
moved: 2026-11-14a
updated: 2026-11-14a
---

List the README under `[guards] reader_docs` in each adopted repo (DEC-340, after DEC-338).

**What:** in audio-workspace, intervals and graph-reachability-zanzibar-index, one repo at a time
and through that repo's own session and procedures: rewrite the README so it cites no record id
(give the reader the words, or point at the board or the records site), add `reader_docs =
["README.md"]` to its `context.toml` `[guards]`, and run its own gate. Each repo needs an engine
pin that has G-D13 (this repo's cdc50a4 or later); bumping the pin is that repo's upgrade step.

**Done when:** all three repos are green with the README listed; residual INV-260 is retired.

## Traps

- Each repo is pushed only with the owner's say-so and its own gate green (DEC-22).

## Read first

- DEC-338, DEC-340; RELEASE-NOTES 0.6's G-D13 upgrade line

## Log
