---
type: Task
id: CE-216
title: 'Carry out DEC-324: committed actors name the model by a normalized display name, not the API id'
pri: LATER
state: open
deps: []
goals: [G-6]
source: session 2026-11-10a
created: 2026-11-10
moved: 2026-11-10a
updated: 2026-11-10c
---

Carry out DEC-324 (owner, answering ASK-37 with option D): committed records name an agent's model by a normalized display name, not its API id.

- The engine derives `<harness>/<name>` (e.g. `claude-code/opus-5.5`) from `CE_ACTOR`'s model at write time, by a mechanical rule (strip `claude-`, dashes to dots, drop a date suffix), never a curated table, so no model can be missing from it.
- The exact id stays in uncommitted session state, where a trial can read it.
- DEC-171's Co-Authored-By derivation reads the same normalized name.
- The contract gains a line saying a repo's CLAUDE.md may narrow the form further (to a role, as ASK-37's option B). Contract wording waits for the next framework version bump.
- Already-pushed records keep their ids and are never rewritten. Give trials (CE-198's numbers, US-23/CE-204) a normalizer that maps old and new actors alike, so grouping by model stays exact.
- Update FRAMEWORK §6.5 ("The model id matters") in place.

## Traps

- Lint and guards that parse `actor:` (G-I3 `ruled_by`, the trailers' `Co-Authored-By` derivation) must accept both forms, since history keeps the old one.

## Read first

- tasks/ASK-37-actor-strings-put-model-ids-into-committed.md (options and the revised recommendation)
- DEC-324, DEC-171, DEC-170

## Log

- 2026-11-10c (claude-code/claude-opus-5-5): fable's second opinion behind option D (2026-11-09, transcribed from the gitignored .scratch/asks-2026-11-09/fable-ask37.md before it was deleted): recommended D with A's contract line, i.e. the default committed actor is <harness>/<normalized display name> (claude-code/opus-5.5), and the exact id stays in uncommitted session state. Why: the harness forbids the identifier but requires a display name in Co-Authored-By, so its intent is 'do not publish API ids', not 'hide which model worked'. D meets both letter and intent; A ships a default that breaks the dominant harness's standing rule in every target repo. Trials lose nothing (claude-opus-5-5 and opus-5.5 carry the same version; only a dated snapshot suffix is dropped, and it can live in session state). Strongest counter: a mapping goes stale with each model release and each non-Claude harness. Mitigation: a mechanical normalization (strip claude-, dashes to dots, drop a date suffix), not a curated table.
