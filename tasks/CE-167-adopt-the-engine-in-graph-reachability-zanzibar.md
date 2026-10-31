---
type: Task
id: CE-167
title: Adopt the engine in graph-reachability-zanzibar-index, after intervals (CE-11)
brief: Not before CE-11 (DEC-134); never push, tag or release zanzibar without the owner's word
pri: LATER
state: open
deps: [CE-11]
goals: [G-6]
source: session 2026-11-01a
created: 2026-11-01
moved: 2026-11-01a
updated: 2026-11-01a
---

Adopt the engine in graph-reachability-zanzibar-index, after intervals (CE-11)

Owner, 2026-11-01a (DEC-134): zanzibar gets its own task, and intervals goes first. zanzibar runs its own board tooling (`scripts/task.py`, `tasks/closed/`) until this lands. Model the work on CE-43: survey the repo (HANDOFF, decision log, board shape, concurrent sessions, its PyPI release flow) before planning the import; back it up first; rehearse the import on a clone; check the import loses no lines; and fold in audio-workspace's open feedback (its `docs/context-engine-feedback.md` item 1: setup also registers the MCP server).

## Traps

- Never push zanzibar, nor tag or release it, without the owner's word: tags there trigger a PyPI release.

## Read first

- CE-43's log (how the audio-workspace cutover went), CE-11, DEC-6, DEC-134

## Log
