---
type: Task
id: CE-22
title: 'Engine commits end with a Session: trailer (pause open today puts the session in the subject only)'
brief: 'DEC-22, FRAMEWORK 6.10: working.py pause_open commit; same for any later engine commit (hk.*)'
pri: NEXT
state: closed
deps: []
source: session 2026-10-10a
created: 2026-10-10
moved: 2026-10-12c
updated: 2026-10-12c
status: deprecated
closed: 2026-10-12c
---

Engine commits end with a Session: trailer (pause open today puts the session in the subject only).

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-12a (claude-code/claude-opus-5-5): manual-mode § pause open gives the same trailer-less commit message, so the hand fallback must change with the engine (paste test, docs/evidence/framework-paste-test-2026-10-12.md).
- 2026-10-12c (claude-code/claude-opus-5-5): closed: Engine.pause_open's commit and manual-mode § pause open both end with a Session: <key> trailer (second -m); the only engine commit site. Tests: test_the_pause_commit_ends_with_a_session_trailer, test_the_runbook_pause_commit_carries_the_same_trailer (both sabotaged red).
