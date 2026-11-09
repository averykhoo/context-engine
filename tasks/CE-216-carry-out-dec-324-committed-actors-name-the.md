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
updated: 2026-11-10a
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
