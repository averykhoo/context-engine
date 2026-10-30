---
type: Task
id: CE-153
title: doc archive refuses the engine's own control files (context.toml, the op log)
brief: 'CE-96 residual (654ea03): both were refused as non-.md before CE-96'
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

doc archive refuses the engine's own control files.

Source: CE-96's close (654ea03), residual (verifier finding 1). `doc archive context.toml` moves the config (every later command then says to create context.toml) and `doc archive docs/ledger/ops.jsonl` moves the op log and starts a new one; both were refused as non-.md before CE-96. Recoverable from git, but nothing refuses it.

## Traps

- none yet

## Read first

- working.py::Engine.doc_archive

## Log
