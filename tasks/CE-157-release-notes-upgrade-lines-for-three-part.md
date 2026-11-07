---
type: Task
id: CE-157
title: 'Release notes: upgrade lines for three-part owner questions and the raised Fan-out cap'
brief: CE-44 (3371106) and CE-107 (8c30e8a) residuals; adopters go red on upgrade otherwise
pri: NOW
state: closed
deps: []
goals: [G-6]
source: session 2026-10-30a
created: 2026-10-31
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

Release notes: upgrade lines for the three-part owner questions and the raised Fan-out cap.

Source: two residuals that ask for a release-notes or upgrade-runbook line; docs/framework/RELEASE-NOTES.md has neither.
- guards.py::ASK_EXEMPT_RE refuses the old template's `none cheap: <why>`; an adopting repo's open questions without the three parts turn G-W4 red on upgrade (kit README § 3 step 4 says so) (CE-44, 3371106).
- Repos that copied the old kit template keep a 90-line Fan-out cap and go G-D1 red when an upgrade replaces fan-out.md, until they raise it (DEC-86; CE-107, 8c30e8a).

## Traps

- none yet

## Read first

- docs/framework/RELEASE-NOTES.md

## Log

- 2026-11-06c (claude-code/claude-opus-5-5): DEC-162: not a floating task but a release step; it waits on the next release and is done as part of it (docs/runbooks/release.md, docs/framework/RELEASE-NOTES.md). No release task is open to dep on, so this comment ties it; dep it on that task when one is filed.
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: Release notes carry upgrade lines for three-part owner questions and the raised Fan-out cap (4221bde); verifier PASS
  residual risk: INV-116
