---
type: Task
id: CE-166
title: adhoc adds gate_receipt to its [working] config
brief: CE-123 follow-up (1fc6b8a); done in the adhoc repo, not here
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

adhoc adds gate_receipt to its [working] config.

Source: CE-123's close (1fc6b8a), follow-up outside this repo. The check (session close refuses, G-W6 fails the newest close, when the guards receipt has no pass count or 'not run') is off until adhoc's context.toml names `gate_receipt`; its register entry 36 came from there. Done in the adhoc repo, not here.

## Traps

- none yet

## Read first

- src/context_engine/kit/context.toml.template

## Log
