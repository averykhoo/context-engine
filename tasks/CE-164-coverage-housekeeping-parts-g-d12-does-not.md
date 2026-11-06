---
type: Task
id: CE-164
title: 'coverage: housekeeping parts G-D12 does not extract, and a frozen map outranking the board'
brief: CE-141 residuals (c5d96b0)
pri: NOW
state: open
deps: []
goals: [G-7]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-05a
updated: 2026-11-06a
---

coverage: housekeeping parts the spec names but G-D12 does not extract, and a frozen map outranking the board.

Source: CE-141's close (c5d96b0), residuals.
- N3 only partly closed: the housekeeping script and hk.close named in FRAMEWORK §8.0.2 and §11.1 are not spec items G-D12 extracts, so they show only through §6.11.
- A DEFERRED or PROSE-ONLY row in the newest map (frozen 2026-10-12) outranks the board: G-T4 reads "deferred" though open CE-34 names it, until a new map is written (guards.py::STATUS_RULES says so).

## Traps

- none yet

## Read first

- guards.py::STATUS_RULES
- ops.py::coverage

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): rerank: Exit criterion 1 (G-7): the coverage op is the milestone's meter. It misses the hk parts, and a stale 2026-10-12 frozen map outranks the board.
- 2026-11-01b (claude-code/claude-opus-5-5): From CE-6's close (DEC-146, 2026-11-01b): coverage still reads G-W10 deferred, because the frozen docs/evidence/framework-coverage-2026-10-12.md marks it DEFERRED and guards.py::_item_status calls a G-id built only when it is in LINT_IDS; G-W10 is hk run's count line (AC-177), not a lint guard. Make coverage read it as built. Also: section 6.11 reads open work while CE-164 and CE-168 are open.
- 2026-11-05a (claude-code/claude-opus-5-5): Owner, 2026-11-05a: "you can just choose whichever task you want for the next NOW". Agent's pick (claude-code/claude-opus-5-5): CE-164, ranked NEXT 1 in the last rerank (docs/evidence/rerank-2026-10-30a.md): the coverage op is the milestone's own meter.
- 2026-11-06a (claude-code/claude-opus-5-5): 602aeac: CE-164: promoted to NOW on the owner's delegation (DEC-158); CE-182 rehearsal clones binned
