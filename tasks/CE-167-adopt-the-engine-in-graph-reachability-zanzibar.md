---
type: Task
id: CE-167
title: Adopt the engine in graph-reachability-zanzibar-index, after intervals (CE-11)
brief: Not before CE-11 (DEC-134); never push, tag or release zanzibar without the owner's word
pri: NOW
state: open
deps: [CE-11]
goals: [G-6]
source: session 2026-11-01a
created: 2026-11-01
moved: 2026-11-03b
updated: 2026-11-03b
---

Adopt the engine in graph-reachability-zanzibar-index, after intervals (CE-11)

Owner, 2026-11-01a (DEC-134): zanzibar gets its own task, and intervals goes first. zanzibar runs its own board tooling (`scripts/task.py`, `tasks/closed/`) until this lands. Model the work on CE-43: survey the repo (HANDOFF, decision log, board shape, concurrent sessions, its PyPI release flow) before planning the import; back it up first; rehearse the import on a clone; check the import loses no lines; and fold in audio-workspace's open feedback (its `docs/context-engine-feedback.md` item 1: setup also registers the MCP server).

## Traps

- Never push zanzibar, nor tag or release it, without the owner's word: tags there trigger a PyPI release.

## Read first

- CE-43's log (how the audio-workspace cutover went), CE-11, DEC-6, DEC-134

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Owner, 2026-11-03b: "Let's do the Zanzibar adoption task" (answering the 2026-11-03a banner's ask: promote CE-167 and start it). Promoted LATER->NOW.
- 2026-11-03b (claude-code/claude-opus-5-5): Session 2026-11-03b: local cutover done and verified. zanzibar branch ce-cutover (worktree C:/Users/user/PycharmProjects/zanzibar-ce-cutover, head 3e63fd7, 7 commits on master 4826a01), engine pin 309641b; 303 board records and 9 decision sections conserved byte-equal (checkers sabotaged); zanzibar's full ten-phase gate green and engine lint clean on 3e63fd7; independent verifier 8/8 PASS. Backup C:/Users/user/zanzibar-backup-2026-11-03 (bundle verified). Nothing pushed, tagged or merged. Waits on the owner: merge-and-push and the design confirmations. Findings: CE-177..CE-181, comments on CE-172, CE-174, CE-56. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md
