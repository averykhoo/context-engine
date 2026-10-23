---
type: Task
id: CE-135
title: 'G-V3: lock gate and background-agent runs per tree, and key the engine write lock on the tree hash or rule it per repo'
brief: FRAMEWORK §5.5 rule 5 asks for tree-hash-keyed locks; only a per-repo engine write lock exists
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-23f
updated: 2026-10-23f
---

FRAMEWORK §5.5 rule 5 and §8.5 G-V3: background agents, gates and engine writes use locks keyed on the tree hash. What exists (2026-10-24): one engine write lock per repo (`lock.py::FileLock`, `[engine] lockfile`); gate runs and background-agent runs take no lock. Filed by CE-93's fix round, which dropped the spec's *Built so far* marker on rule 5 (CE-17 was cited for the gate lock; nothing tracked the write lock's key).

Two parts:
1. A lock on gate runs and background-agent runs for the same tree (CE-17's run ledger runs under it).
2. The engine write lock: key it on the tree hash, or have the owner rule that one per repo is the standard (a rule change: a decision record and a RELEASE-NOTES line, and `docs/engine.md` § The engine lock updated).

## Traps

- A write lock keyed on the tree hash changes key with every write; check what "the same tree" means for writes before building part 2.

## Read first

- `docs/framework/FRAMEWORK.md` §5.5 rule 5, §8.5 G-V3; `docs/engine.md` § The engine lock

## Log
