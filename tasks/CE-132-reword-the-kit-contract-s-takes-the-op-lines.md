---
type: Task
id: CE-132
title: Reword the kit contract's 'takes the op lines still uncommitted' at the next contract version bump (CE-125)
brief: 'Wait for a version bump: changing it now turns G-D0 red in every adopting repo'
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-22b
created: 2026-10-22
moved: 2026-10-22b
updated: 2026-10-30a
---

Reword the kit contract's 'takes the op lines still uncommitted' at the next contract version bump (CE-125).

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-23f (claude-code/claude-opus-5-5): Also at the same bump (CE-113 verify-1, non-blocking 5): the kit contract's 'Who decides' sentence 'A call the owner delegates ("you decide") is still the one who made it' is hard to parse; reword to something like 'is still the call of whoever made it' (added by CE-113, 21a88d9).
- 2026-10-30a (claude-code/claude-opus-5-5): From CE-84 (7920cbd, DEC-105): kit/contract.md § Procedures 'More work asked for after the close starts a new session' could add 'with `session start --follows <key>` when it fixes what the closed session left'. Not edited by CE-84, because the contract is held.
