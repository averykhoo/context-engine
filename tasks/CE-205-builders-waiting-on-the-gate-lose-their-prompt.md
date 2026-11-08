---
type: Task
id: CE-205
title: "Builders waiting on the gate lose their prompt cache: about 20% of a session's cost"
pri: LATER
state: open
deps: []
goals: [G-1]
source: session 2026-11-07e
created: 2026-11-08
moved: 2026-11-07e
updated: 2026-11-07e
---

Builders that wait on the gate lose their prompt cache (US-23 cost anatomy, 2026-11-08).

docs/evidence/us23-planner-and-cost-2026-11-08.md: every gap of more than 300 seconds between an agent's turns was a full cache miss (63 of 63), and all of them were builders waiting on the whole gate (one run took 887 s on 2026-11-07e). Those misses cost about $45 of the session's $225, about 20%. The cache's TTL is 5 minutes.

Options to weigh (none tested):
- The agent runs the gate in the background and checks on it at most every 4.5 minutes, so each check re-reads the cached prefix and keeps it warm.
- A faster gate: run only the tests the change can reach, as CE-17 proposes, with the whole gate kept for pushes and closes.
- Where the harness allows it, a 1-hour cache TTL: the anatomy's estimate is that this roughly breaks even.

The method lesson, if one is adopted, goes in docs/runbooks/fan-out.md and its kit copy (byte-equal).

## Traps

- A poll that runs the gate again, instead of reading the running one's output, doubles the cost it saves.

## Read first

- docs/evidence/us23-planner-and-cost-2026-11-08.md (§ Cache misses)
- CE-17
