---
type: Task
id: CE-173
title: 'Adopter CI: engine writes defeat docs-only CI filters'
brief: Seen in CE-11; intervals needed gate.py and fuzz.yml changes (commit 3906abd)
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-02a
updated: 2026-11-02a
---

From CE-11 (2026-11-02a): the op log is .jsonl, so a repo whose CI skips **.md changes runs full CI on every engine write; doc archive writes docs/archive/README.md, which gates that treat README files specially (intervals doctest scope) see as a code change. At least the kit README should warn adopters and name the paths to treat as prose (context.toml, docs/ledger/**, docs/archive/**).
