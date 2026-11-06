---
type: Task
id: CE-192
title: gate_receipt on by default in the engine (DEC-162 amends DEC-107)
brief: 'DEC-162: supersede DEC-107 when built; release note for repos whose gate prints no pass count'
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-11-06c
created: 2026-11-06
moved: 2026-11-06c
updated: 2026-11-06c
---

gate_receipt on by default in the engine (DEC-162 amends DEC-107).

Source: DEC-162, adopting docs/evidence/owner-review-advice-2026-11-06b.md § 3 (DEC-107: **on**). DEC-107 chose (b), engine default off with the kit template and this repo opting in. The owner's ruling is the engine default on, so a repo that never opted in (adhoc) goes red until it adds a receipt: a check that is off where nobody opted in is the house failure mode.

Scope: the engine default for `[working] gate_receipt` becomes the kit value; a release-notes upgrade line says repos whose gate prints no pass count must set it; record the build as a decision that supersedes DEC-107 (`decision supersede DEC-107 <new>`). CE-166 (adhoc) then needs only its receipt line.

## Traps

- An upgrade turns closes red in a repo whose gate prints no 'N passed' (e.g. go test): that is the ruling's intent; say so in RELEASE-NOTES.

## Read first

- DEC-107
- DEC-162

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): Filed at LATER, not NEXT: NEXT holds the five DEC-162 names (cap 5). Agent's call, PROVISIONAL; promote when a slot frees.
