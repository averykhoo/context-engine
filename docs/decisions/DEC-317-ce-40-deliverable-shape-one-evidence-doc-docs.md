---
type: Decision
id: DEC-317
title: 'CE-40 deliverable shape: one evidence doc docs/evidence/global-claude-md-audit-<session>.md, ACTIVE-PLAN naming only CE-40, with the trimmed global text as one 4-backtick fenced block in its section 4; no separate raw file, no tracked test'
tasks: [CE-40]
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:7e8e9465326fbcc0b8c3dc7c8aa11d9f6bc3c2e14d0c1f989443a0c597923610
---

An agent's call under P8 (cheap to undo: one tracked doc, a local commit), made by CE-40's builder in session 2026-11-07e on 2026-11-08, following the planner's design. Not owner words.

CE-40's deliverable is one evidence doc, `docs/evidence/global-claude-md-audit-2026-11-07e.md`, whose ACTIVE-PLAN line names only CE-40, so G-D4 (guards.py::liveness) holds the freeze to CE-40's close. The proposed trimmed global `CLAUDE.md` is one 4-backtick fenced block in its section 4, because the text holds bash and powershell fences.

Rejected: a separate raw-text file (two files to keep in step, a second liveness line); a tracked test pinning the doc's quotes to FRAMEWORK (the doc freezes when CE-40 closes, and frozen provenance is never edited, so a pin would either force an edit to it or go red on every FRAMEWORK rewording). The doc's section 5 carries its throwaway checker's code and dated output instead, so the check can be re-run.
