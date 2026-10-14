---
type: Task
id: CE-68
title: 'Phrasing sweep: rituals become procedures, and every strange turn of phrase in the framework is corrected at once'
brief: DEC-39; living text only; one change; terms that ripple into code or decisions go to the owner
pri: NEXT
state: closed
deps: []
source: session 2026-10-13e
created: 2026-10-13
moved: 2026-10-13e
updated: 2026-10-13e
status: deprecated
closed: 2026-10-13e
---

## What

DEC-39: rename "rituals" to "procedures" everywhere it is living text, and in the same change
correct every strange turn of phrase across the framework, all at once.

## Scope

- In: FRAMEWORK.md; the kit (contract, README, bootloader, runbooks, templates, HANDOFF skeleton)
  and this repo's byte copies; CLAUDE.md, HANDOFF.md, charter, criteria, context.toml comments;
  user-facing strings in src/; tests and tools that pin the words; open board items.
- Out (frozen provenance or append-only, never edited): decisions, stories, the ledger and op log,
  docs/evidence, spike/, FRAMEWORK-v0.5.md, closed board items, register entries.
- `rituals.md` becomes `procedures.md` (repo and kit), with its routes, links, anchors and the
  tests that pin it. No repo has adopted the kit yet (CE-7 is next), so there is no upgrade path.

## Method

A census fan-out over the in-scope text finds candidates (phrase, place, why it reads oddly, a
rewrite). The top level reviews the list. A term that ripples into code, config or a recorded
decision (an id prefix, a kind name) goes to the owner rather than being changed. Then everything
accepted is applied in one change, gated on Windows and on `tools/linux_gate.py`.

Traps:
- byte-equal pairs: docs/runbooks/* and src/context_engine/kit/docs/runbooks/*;
  docs/framework/contract.md and src/context_engine/kit/contract.md (G-D0)
- G-D5 counts in prose; G-D4 liveness lines in the first 10 lines
- a heading rename changes its anchor: grep every `#anchor` link

## Log

- 2026-10-13e (claude-code/claude-opus-5-5): closed: done in 0f1d071: rituals are procedures; the phrasing sweep applied in one change
