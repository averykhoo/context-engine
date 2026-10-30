---
type: Task
id: CE-161
title: The commit op names an unparseable record and refuses only for records it carries
brief: CE-134 residual (d6a2fa5); a hand edit is legal and caught by lint, not by a crash
pri: LATER
state: open
deps: []
goals: [G-5]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-10-30a
updated: 2026-10-30a
---

The commit op names an unparseable record and refuses only for the records it carries.

Source: CE-134's close (d6a2fa5), residual. Through the `commit` op the first refusal on a broken record comes from lint raising (store.py::Store.heads reads every board record's frontmatter), so it names the YAML error but not the file, and it refuses even when the broken record is not one the commit would carry; lint could report an unparseable record as a failure instead.

## Traps

- none yet

## Read first

- store.py::Store.heads
- commit.py::select

## Log
