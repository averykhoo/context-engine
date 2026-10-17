---
type: Question
id: ASK-13
title: 'audio-workspace init choices: settings merge or skip, task prefix, push the pre-context-engine tag?'
brief: 'Rec: --merge-settings (DEC-32), task prefix AW, push the tag to GitLab before the cutover'
pri: LATER
state: open
deps: []
source: session 2026-10-17b
created: 2026-10-17
moved: 2026-10-17b
updated: 2026-10-17b
last_asked: 2026-10-17b
blocks: [CE-43]
---

init needs --merge-settings or --skip-settings because .claude/settings.local.json exists (DEC-32). A task prefix that cannot collide with D-n or the engine's own ids. The backup tag only protects against loss of this laptop if it is pushed.
