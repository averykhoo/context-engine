---
type: Task
id: CE-56
title: 'Standard id prefixes (DEC-38): kit defaults, init asks the task prefix, reserved prefixes in lint, this repo renamed'
brief: 'Ids are never renumbered: a rename keeps the number and the old id stays an alias (DEC-37); stamped text keeps old ids'
pri: LATER
state: open
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
---

DEC-38 sets one prefix per record kind in every repo, 2 to 5 capitals: DEC, STORY, AC, ASK, RISK, GOAL, BATON, PAUSE; EXP and HAZ reserved; tasks a per-repo prefix (CE here). Scope: the kit template's [kinds.*] prefixes (today D, S, T, ASK, BTN, PAU) and the criteria, register and goal id forms move to the standard set; init asks for the task prefix instead of defaulting to T; lint refuses a task prefix equal to a standard or reserved one; FRAMEWORK P3 names the set; guards that read goal ids read GOAL-n (and the legacy G-n and Gn). This repo renames US -> STORY, INV -> RISK, G -> GOAL, BTN -> BATON, PAU -> PAUSE through DEC-37's alias mechanism, as its first trial before adhoc (agent's reading of DEC-35 and DEC-37; the owner has not said this repo renames, so confirm before the rename step). Order: after CE-7 builds aliases, or this item builds them first.
