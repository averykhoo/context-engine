---
type: Question
id: ASK-4
title: 'CE-38: where does the SessionStart hook live: a machine-local settings file init creates, or the committed .claude/settings.json?'
brief: 'Recommend (a): init creates .claude/settings.local.json with absolute paths, only when absent; built as (a)'
pri: LATER
state: open
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13b
last_asked:
---

CE-38 needs a SessionStart hook that runs `context-engine orient`. The hook command must name the engine's interpreter, which is machine-specific (the engine runs from its own environment, DEC-1; on this machine `context-engine` is not on PATH).

Options:
(a) init writes `.claude/settings.local.json` (machine-local, gitignored; `.claude/.gitignore` is created too) with absolute paths to the engine's interpreter and the repo root. Works on the machine that ran init with no further setup; another clone or machine needs it again (as `claude mcp add --scope local` does). init creates the file only when absent; an existing one is left alone and init's line names the kit README section with the JSON to merge by hand.
(b) a committed `.claude/settings.json` hook that calls `context-engine` on PATH, or `$CE_PYTHON`: every clone gets it, but it fails quietly wherever the script is not on PATH or the variable is unset (both true on this machine today).
(c) as (a), but init also merges the hook into an existing settings.local.json (JSON rewrite of a file that holds the owner's permission grants).

Recommendation: (a). Built as (a) so CE-7 can go ahead; reversible (the hook text is in one place, bootstrap.py, and the kit README). Filed at LATER only because NEXT is full (5 of 5); raise it in chat.
