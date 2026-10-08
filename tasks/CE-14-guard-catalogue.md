---
type: Task
id: CE-14
title: "The guard catalogue (FRAMEWORK §8.1 to §8.5) as engine lint guards"
brief: "Minimum set first (§11.1); every guard sabotaged red before it is believed; each docstring says what it does not check"
pri: LATER
state: open
deps: [CE-2]
source: session 2026-10-08b
created: 2026-10-08
moved: 2026-10-08b
updated: 2026-10-08b
closed:
---

The engine's lint framework (CE-1, CE-2) carries the record-level guards; this item builds the
rest of the catalogue: intent (G-I), trace and existence (G-T), doc (G-D), working-state (G-W)
and verification-state (G-V) guards. Start with the §11.1 minimum set, then the §11.2 triggers
this repo actually hits. Part of G7 (DEC-10).

## Traps

- A guard that fails by passing is the house failure mode: sabotage each one and watch it go
  red before claiming it.
- Existing repos keep their own check numbers; the package maps onto them (§8.0, P3).

## Read first

- `docs/framework/FRAMEWORK.md` §8.0, §8.1 to §8.5, §11.1, §11.2

## Log
