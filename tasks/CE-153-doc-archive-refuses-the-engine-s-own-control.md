---
type: Task
id: CE-153
title: doc archive refuses the engine's own control files (context.toml, the op log)
brief: 'CE-96 residual (654ea03): both were refused as non-.md before CE-96'
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-06c
updated: 2026-11-06c
status: deprecated
closed: 2026-11-06c
---

doc archive refuses the engine's own control files.

Source: CE-96's close (654ea03), residual (verifier finding 1). `doc archive context.toml` moves the config (every later command then says to create context.toml) and `doc archive docs/ledger/ops.jsonl` moves the op log and starts a new one; both were refused as non-.md before CE-96. Recoverable from git, but nothing refuses it.

## Traps

- none yet

## Read first

- working.py::Engine.doc_archive

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): closed: merged into CE-154 (DEC-162): same file, a one-line refusal; CE-154 carries it
  residual risk: none
