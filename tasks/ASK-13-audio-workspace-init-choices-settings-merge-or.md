---
type: Question
id: ASK-13
title: 'audio-workspace init choices: settings merge or skip, task prefix, push the pre-context-engine tag?'
brief: 'Rec: --merge-settings (DEC-32), task prefix AW, push the tag to GitLab before the cutover'
pri: LATER
state: closed
deps: []
source: session 2026-10-17b
created: 2026-10-17
moved: 2026-10-17b
updated: 2026-10-17c
last_asked: 2026-10-17c
blocks: [CE-43]
status: deprecated
closed: 2026-10-17c
answered: {on: 2026-10-17, session: 2026-10-17c, decision: DEC-59}
---

init needs --merge-settings or --skip-settings because .claude/settings.local.json exists (DEC-32). A task prefix that cannot collide with D-n or the engine's own ids. The backup tag only protects against loss of this laptop if it is pushed.

## Log

- 2026-10-17c (claude-code/claude-opus-5-5): answered by the owner: DEC-59
