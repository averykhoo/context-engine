---
type: Task
id: CE-146
title: Plugin launcher stays quiet when any settings hook mentions orient, even a stale one with another machine's path that fails silently
brief: From CE-77's review (LOW), split out of CE-85 on 2026-10-30a
pri: LATER
state: open
deps: []
goals: [G-4]
source: session 2026-10-30a
created: 2026-10-30
moved: 2026-10-30a
updated: 2026-10-30a
---

Plugin launcher stays quiet when any settings hook mentions orient, even a stale one with another machine's path that fails silently.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): From CE-77's review (session 2026-10-15a, LOW), carried in CE-85's body and left out of its fix: the plugin launcher stays quiet when any settings hook's command mentions context_engine ... orient, including a stale one with another machine's path in a committed .claude/settings.json, which then fails silently.
