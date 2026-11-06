---
type: Task
id: CE-195
title: 'Cheap sessions: banner holds only durable lines, session close is one call, session start --continues (DEC-163, US-21)'
brief: 'DEC-163: close eagerly stays; make the close cheap. Keep its safety: a dead session never looks live'
pri: NOW
state: closed
deps: []
goals: [G-1, G-3]
source: session 2026-11-06f
created: 2026-11-06
moved: 2026-11-06f
updated: 2026-11-06f
status: deprecated
closed: 2026-11-06f
---

Make a session cheap enough that closing after every reply costs seconds (DEC-163, US-21, AC-185).

1. Banner: stop hand-writing what orient already generates or could read from the records (NOW/NEXT, open asks, push and upstream state, the review queue). The banner keeps durable hand-written lines only, and a clean close need not rewrite it when nothing durable changed (G-W1). The last close's digest is shown by orient instead of being copied into the banner.
2. session close does it in one call: the close housekeeping (hk run close) and the ledger entry; the banner only when given.
3. session start --continues <key>: a session started after a close in the same conversation links back to it, so a back-and-forth reads as one thread.

Evidence (2026-11-06): five sessions in one conversation (06a..06f); two of four banner rewrites went wrong (line offsets, a width refusal), the banner went over orient's cap, and a close summary claimed a trim that was not done.

## Traps

- none yet

## Read first

- docs/decisions/DEC-163-close-eagerly-stays-with-no-long-lived-session.md
- docs/stories/US-21-close-eagerly-fits-ephemeral-conversations-long.md

## Log

- 2026-11-06f (claude-code/claude-opus-5-5): closed: built and verified (independent PASS, round 3): durable-only banner with banner: kept, one-call session close, session start --continues; gate 1464 passed
  residual risk: INV-99
