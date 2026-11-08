---
type: Task
id: CE-56
title: 'Standard id prefixes (DEC-38): kit defaults, init asks the task prefix, reserved prefixes in lint'
brief: 'Ids are never renumbered: a rename keeps the number and the old id stays an alias (DEC-37); stamped text keeps old ids'
pri: NOW
state: closed
deps: []
source: session 2026-10-13c
created: 2026-10-13
moved: 2026-11-07e
updated: 2026-11-07e
goals: [G-6]
status: deprecated
closed: 2026-11-07e
---

DEC-38 sets one prefix per record kind in every repo, 2 to 5 capitals: DEC, STORY, AC, ASK, RISK, GOAL, BATON, PAUSE; EXP and HAZ reserved; tasks a per-repo prefix (CE here). Scope: the kit template's [kinds.*] prefixes (today D, S, T, ASK, BTN, PAU) and the criteria, register and goal id forms move to the standard set; init asks for the task prefix instead of defaulting to T; lint refuses a task prefix equal to a standard or reserved one; FRAMEWORK P3 names the set; guards that read goal ids read GOAL-n (and the legacy G-n and Gn). This repo renames US -> STORY, INV -> RISK, G -> GOAL, BTN -> BATON, PAU -> PAUSE through DEC-37's alias mechanism, as its first trial before adhoc (agent's reading of DEC-35 and DEC-37; the owner has not said this repo renames, so confirm before the rename step). Order: after CE-7 builds aliases, or this item builds them first.

## Log

- 2026-10-14a (claude-code/claude-opus-5-5): Audit 2026-10-14a (spec F6, F7): the engine does not enforce [A-Z]+-[1-9][0-9]* on prefixes; init accepts digits and its remedy suggests T2; G and INV prefixes are hard-coded. Fold into this task's prefix work.
- 2026-11-03b (claude-code/claude-opus-5-5): From CE-167: the kit's default prefixes D and S collide with ordinary audit labels (zanzibar's D7, S-1..S-7) and init --dry-run gives no warning; zanzibar took DEC/TK/US. Idea: census <prefix>-<n> hits in the tracked tree during the dry run. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md § Engine findings
- 2026-11-06c (claude-code/claude-opus-5-5): DEC-162: the rename half (this repo's US, INV, G, BTN, PAU to STORY, RISK, GOAL, BATON, PAUSE) is declined: DEC-37's aliases exist so this repo keeps its prefixes while the kit defaults use the standard set. The kit-defaults half stands (template prefixes, init asking the task prefix, reserved prefixes in lint, the prefix census idea), so the task stays open.
- 2026-11-06c (claude-code/claude-opus-5-5): Title drops 'this repo renamed': that half was declined (DEC-162).
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: standard id prefixes: kit defaults DEC/STORY/AC/ASK/RISK/GOAL/BATON/PAUSE, init asks the task prefix, lint refuses standard and reserved task prefixes, goal ids GOAL-n/G-n/Gn are one goal. Work: 21a61af 426f61a 69ce8ff ea3781b; engine commits of DEC-229..DEC-236: 980e927 690eb10 63aa89d 70f737a 48e0d78 7b1e4ed fadea4d 5984bb7. Independent verifier PASS.
  residual risk: INV-170, INV-171, INV-172, INV-173, INV-174, INV-175
