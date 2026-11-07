---
type: Task
id: CE-173
title: 'Adopter CI: engine writes defeat docs-only CI filters'
brief: Seen in CE-11; intervals needed gate.py and fuzz.yml changes (commit 3906abd)
pri: NEXT
state: closed
deps: []
goals: [G-6]
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

From CE-11 (2026-11-02a): the op log is .jsonl, so a repo whose CI skips **.md changes runs full CI on every engine write; doc archive writes docs/archive/README.md, which gates that treat README files specially (intervals doctest scope) see as a code change. At least the kit README should warn adopters and name the paths to treat as prose (context.toml, docs/ledger/**, docs/archive/**).

## Log

- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: kit README § 5 names the engine writes a docs-only CI filter misses (fdeb0b5)
  residual risk: none
