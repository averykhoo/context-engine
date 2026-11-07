---
type: Task
id: CE-189
title: 'Two decision-conflict checks: duplicate live titles, and a relates/narrows link kind'
brief: 'DEC-162: mechanical checks only, no semantic conflict detection'
pri: NOW
state: open
deps: []
goals: [G-2]
source: session 2026-11-06c
created: 2026-11-06
moved: 2026-11-07e
updated: 2026-11-07e
---

Two mechanical decision-conflict checks: duplicate live titles, and a relates/narrows link kind (DEC-162).

Source: DEC-162, adopting docs/evidence/owner-review-advice-2026-11-06b.md § 2.2. No semantic conflict detection. Two cheap checks:
- lint fails two non-superseded decisions with the same title (the DEC-91/DEC-92 case);
- a `relates:`/`narrows:` link kind, so pairs such as DEC-126 and DEC-112 are links, not prose.

## Traps

- none yet

## Read first

- docs/evidence/owner-review-advice-2026-11-06b.md § 2

## Log

- 2026-11-07e (claude-code/claude-opus-5-5): Built (uncommitted, for verification): new intent guard G-I4 (guards.py::decision_titles, FRAMEWORK §8.1), two current decisions with one title; the relates/narrows half was already built in CE-5 as `refs` and `relaxes`/`narrowed_by`, so only working.py::Engine._link_rel remedy and manual-mode § context-engine decision link now name `--rel refs`. AC-191; DEC-214 to DEC-217.
