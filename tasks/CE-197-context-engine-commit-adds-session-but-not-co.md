---
type: Task
id: CE-197
title: 'context-engine commit adds Session: but not Co-Authored-By:, so agent commits miss the trailer CLAUDE.md requires'
brief: 'CE-64 trailer paragraph: Session and Co-Authored-By, no blank line between'
pri: LATER
state: open
deps: []
goals: [G-3]
source: session 2026-11-06f
created: 2026-11-06
moved: 2026-11-06f
updated: 2026-11-06f
---

Seen 2026-11-06f: every `context-engine commit` and engine milestone commit today carried `Session:` alone (962b4b3, 243efd0 pushed; 6b9278d, e4489f0, 8d05a1c local), against CLAUDE.md § Rules (CE-64): one trailer paragraph with Session: and Co-Authored-By:. Hand-amending to add it also nearly split the paragraph with a blank line (which would leave the commit foreign). Fix: the op takes the harness's Co-Authored-By line (config or env) and writes it into the same trailer paragraph; lint or a test checks a commit's last paragraph.

## Traps

- A blank line between Session: and Co-Authored-By: makes git read only the last paragraph, so Session: is lost.

## Read first

- none yet

## Log
