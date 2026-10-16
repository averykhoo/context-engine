---
type: Task
id: CE-93
title: Archive FRAMEWORK.md, then rewrite it as what is needed to understand and use the framework (DEC-49)
brief: Archive first (§6.12); no history, no prior art, no build status in the new text; section numbers stay stable (P3)
pri: NOW
state: open
deps: []
source: session 2026-10-15c
created: 2026-10-15
moved: 2026-10-16a
updated: 2026-10-16a
---

DEC-49 (owner): FRAMEWORK.md should be "what's needed to understand and use the framework, not what's needed to be a historian". It also approves dedupe-2.

Steps:
1. Archive the current text per §6.12: copy it to `docs/framework/FRAMEWORK-v<version>.md`, opened `ARCHIVED <date>`.
2. Rewrite for a user of the framework:
   - Cut origin stories, dated incident prose ("seen 2026-10-13"), regulation background beyond what a rule needs, and the "why" that lives in decisions. Keep the pointer instead (a decision id; an incident id once the DEC-47 task lands).
   - **dedupe-2:** remove every *Not built yet (CE-n)* and *Built so far* marker. Build status is on the board (§8.0.3 already says so). Where a reader must know a part is unavailable, consider a generated status table from task state instead.
   - Separate the standard (what must hold) from engine internals (how the engine does it, e.g. §5.5 rule 4's git-environment cases), which can go to engine docs or a runbook.
3. Keep section numbers stable (P3), and give the version release notes (which rules changed, and why, by decision id) for adopting repos.

This likely absorbs CE-89 (frozen wording owed after CE-41 and CE-87).

## Traps
- A FRAMEWORK edit: wait for the CE-7 hold, or ask.
- Section numbers are cited across records: a missing number stays missing, never renumbered.
- Guards read FRAMEWORK (the coverage map from CE-30, G-D4 liveness, AC-33's §6.6 text): run the gate after each cut.

## Read first
- docs/decisions/DEC-49-framework-md-holds-what-is-needed-to-understand.md
- docs/framework/FRAMEWORK.md §6.12, §7.3

## Log

- 2026-10-15c (claude-code/claude-opus-5-5): "the DEC-47 task" in the body is CE-94 (incident citations).
- 2026-10-15e (claude-code/claude-opus-5-5): DEC-50 (owner, 2026-10-15e): stays held until the trial's feedback is in (CE-79, about 2026-10-21), so the text is not rewritten twice.
- 2026-10-16a (claude-code/claude-opus-5-5): Owner (2026-10-16a) picked it as NOW after CE-27 closed; that lifts the CE-7 kit-edit hold for it. CE-27's doc archive op can do the archive step.
