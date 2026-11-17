---
type: Task
id: CE-246
title: init's .claude/.gitignore also ignores worktrees/
pri: LATER
state: open
deps: []
goals: [G-4]
source: session 2026-11-17b
created: 2026-11-17
moved: 2026-11-17b
updated: 2026-11-17b
---

init's .claude/.gitignore also ignores worktrees/.

adhoc-microphone-array (AD-112 item 24): `init` writes `.claude/.gitignore` with `settings.local.json` only (bootstrap.py::_ensure_ignore), so Claude Code's `.claude/worktrees/` shows as untracked in every adopter until added by hand. This repo's own `.claude/.gitignore` has the line. docs/evidence/engine-feedback-2026-11-17.md, F24.

## Traps

- Append the line to an existing file without duplicating it, as the current entry is handled; existing adopters get it through CE-240's checklist or by hand (adhoc's CE-241 step).

## Read first

- docs/evidence/engine-feedback-2026-11-17.md: F24
- bootstrap.py::_ensure_ignore

## Log
