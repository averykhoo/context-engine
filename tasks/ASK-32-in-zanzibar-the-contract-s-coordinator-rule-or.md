---
type: Question
id: ASK-32
title: In zanzibar, the contract's coordinator rule or CLAUDE.md's 'the session works'?
brief: 'Recommend: the coordinator rule'
pri: LATER
state: open
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-03b
last_asked: 2026-11-03b
---

## Context

Zanzibar's CLAUDE.md says the session does the work itself; the framework contract it now imports says the
top-level session coordinates and pushes every task to subagents. CLAUDE.md wins where it narrows the
contract, but the builder left this conflict for the owner rather than ruling on it. (Zanzibar's CLAUDE.md
also allows fable for executive decisions; it now says that overrides the contract's no-fable default.)

## Options

- Zanzibar adopts the coordinator rule (its CLAUDE.md line is removed).
- Zanzibar keeps "the session works" (CLAUDE.md says so explicitly as an override).

## Recommendation

The coordinator rule: zanzibar's sessions are long and context-heavy, which is the case the rule was made for.
