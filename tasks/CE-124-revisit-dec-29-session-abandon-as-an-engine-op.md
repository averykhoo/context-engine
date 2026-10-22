---
type: Task
id: CE-124
title: 'Revisit DEC-29: session abandon as an engine op'
brief: Adhoc trial abandoned stale stubs by hand 3 times; decide on a session abandon op or keep DEC-29
pri: LATER
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-22b
updated: 2026-10-22b
status: deprecated
closed: 2026-10-22b
---

Revisit DEC-29: session abandon as an engine op

What went wrong (adhoc AAR entries 3 and 25, docs/evidence/adhoc-feedback-2026-10-21.md): abandoning a stale session stub was done by hand three times in the adhoc trial, and clean close does not retire a dead session's stub. DEC-29 (PROVISIONAL) keeps abandoning a by-hand rule "until we need to work it out"; the recurrences are that need. Decide whether to add a `session abandon` op that close offers for a dead session (with last activity from CE-104 as the evidence), or confirm the by-hand rule; no new decision is filed here, the owner's answer amends or supersedes DEC-29. Related: CE-6 (hk stale-stub abandon), CE-104. Census F3: DEC-29 keeps by hand; reopen.

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md
- docs/decisions/DEC-29-abandoning-a-stale-session-stub-stays-a-by-hand.md

## Log

- 2026-10-22b (claude-code/claude-opus-5-5): closed: done in e74be36
