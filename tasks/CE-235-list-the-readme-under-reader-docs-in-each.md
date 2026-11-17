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
updated: 2026-11-17a
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

- 2026-11-16b (claude-code/claude-opus-5-5): intervals and zanzibar done locally, no push (agent report .scratch/ce-235/agent.md). Both bumped from pin 309641b (0.5) to 989982a (0.6) by kit README §4; README cites no record id; reader_docs = [README.md]; own gates green; Sabotage: an id put back in README -> G-D13 red in each. intervals: 5b5c011, baf3269, ed10d54 (D-46 retitled for G-I4, agent's call). zanzibar: ebf71d8, f3e1037, fae13a2 (banner cut to durable lines; DEC-13..15 accepted --owners). Left: audio-workspace (another session's uncommitted work), pushes of both repos on the owner's say-so, old envs .context-engine/env-309641b to delete, then retire INV-260.
- 2026-11-17a (claude-code/claude-opus-5-5): pushed (owner 2026-11-17: 'push the changes'): intervals ed10d54 (prepush green: docs only, nothing to run; CI ci green, fuzz skipped by paths-ignore), zanzibar fae13a2 (ten-phase gate covered; CI gate 10/10 and docs green). audio-workspace remains.
