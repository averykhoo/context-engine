---
type: Question
id: ASK-12
title: 'audio-workspace: engine-green means tsc + lint only (scope all), with vitest and smoke run before push by the testing runbook, unrecorded by the engine?'
brief: "Rec: yes; it matches today's convention (no hook), and CLAUDE.md says so in plain words"
pri: LATER
state: open
deps: []
source: session 2026-10-17b
created: 2026-10-17
moved: 2026-10-17b
updated: 2026-10-17b
last_asked: 2026-10-17b
blocks: [CE-43]
---

Follows DEC-51 (vitest and smoke before push, not per commit). The engine's [gate] holds one command; its readers and scope guard work only with pytest. Scope 'all' with a seconds-long command re-runs after every record write and cannot go stale silently. The push gate stays the testing runbook's, as today.
