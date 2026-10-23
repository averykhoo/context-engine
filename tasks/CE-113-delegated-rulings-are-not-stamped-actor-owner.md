---
type: Task
id: CE-113
title: 'Delegated rulings are not stamped actor: owner; separate owner words from a ruling made on delegation'
brief: A ruling taken on delegation must not be stamped owner or sit inside an owner quote (frozen); add ruled_by
pri: NEXT
state: closed
deps: []
goals: [G-2]
source: session 2026-10-21b
created: 2026-10-21
moved: 2026-10-23f
updated: 2026-10-23f
status: deprecated
closed: 2026-10-23f
---

Delegated rulings are not stamped actor: owner; separate owner words from a ruling made on delegation

What went wrong (adhoc AAR entry 24, docs/evidence/adhoc-feedback-2026-10-21.md) and what to change: A decision taken on the owner's delegation was stamped `actor: owner` and its text sat inside the owner-quote block, which is frozen, so the agent's reasoning became unamendable owner words (entry 24). Separate the owner's words from the ruling, and record who ruled (`ruled_by`, with the delegating quote). Census F16: NEW, severity high. Filed 2026-10-21b from the CE-7 census (.scratch/ce7-feedback/census.md, row F16).

## Traps

## Read first

- docs/evidence/adhoc-feedback-2026-10-21.md

## Log

- 2026-10-23f (claude-code/claude-opus-5-5): Owner, 2026-10-23f (DEC-72): freeze lifted; work CE-113, then CE-93.
- 2026-10-23f (claude-code/claude-opus-5-5): Built (uncommitted, for verification): `ruled_by` on decisions, `ask answer --ruling/--ruling-file --ruled-by`, the `## Ruling` section, and lint guard G-I3 (delegated rulings), with record new's and ask answer's write-time twins; FRAMEWORK §5.3, §6.2, §6.5, §8.1 and the kit runbooks updated; AC-98 to AC-100. Report: .scratch/ce-113/build.md
- 2026-10-23f (claude-code/claude-opus-5-5): closed: Fixed in 21a88d9: delegated rulings record ruled_by and a ## Ruling section, actor 'owner asked'; lint G-I3 plus write-time refusals in record new and ask answer
