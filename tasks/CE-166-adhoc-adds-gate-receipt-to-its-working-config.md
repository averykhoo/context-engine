---
type: Task
id: CE-166
title: adhoc adds gate_receipt to its [working] config
brief: CE-123 follow-up (1fc6b8a); done in the adhoc repo, not here
pri: LATER
state: open
deps: [CE-192]
goals: [G-6]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-11-06c
---

adhoc adds gate_receipt to its [working] config.

Source: CE-123's close (1fc6b8a), follow-up outside this repo. The check (session close refuses, G-W6 fails the newest close, when the guards receipt has no pass count or 'not run') is off until adhoc's context.toml names `gate_receipt`; its register entry 36 came from there. Done in the adhoc repo, not here.

## Traps

- none yet

## Read first

- src/context_engine/kit/context.toml.template

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): DEC-162 rules gate_receipt on by default in the engine (CE-192). Once CE-192 ships, adhoc goes red until it sets a receipt that matches its gate output, so this task is just adding that one [working] gate_receipt line in adhoc's context.toml, first thing in the next adhoc session; then close it here.
