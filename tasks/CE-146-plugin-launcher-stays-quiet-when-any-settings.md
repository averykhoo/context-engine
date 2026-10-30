---
type: Task
id: CE-146
title: Plugin launcher stays quiet when any settings hook mentions orient, even a stale one with another machine's path that fails silently
brief: From CE-77's review (LOW), split out of CE-85 on 2026-10-30a
pri: NOW
state: closed
deps: []
goals: [G-4]
source: session 2026-10-30a
created: 2026-10-30
moved: 2026-10-30a
updated: 2026-10-30a
status: deprecated
closed: 2026-10-30a
---

Plugin launcher stays quiet when any settings hook mentions orient, even a stale one with another machine's path that fails silently.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): From CE-77's review (session 2026-10-15a, LOW), carried in CE-85's body and left out of its fix: the plugin launcher stays quiet when any settings hook's command mentions context_engine ... orient, including a stale one with another machine's path in a committed .claude/settings.json, which then fails silently.
- 2026-10-30a (claude-code/claude-opus-5-5): closed: CE-146: the plugin launcher now stays quiet only beside a settings orient hook that can run on this machine. Its program must be a file here or a bare name on PATH, and its --root, when it names one, must be this repo. A program or --root that names a variable ($CLAUDE_PROJECT_DIR, %VAR%) or starts with ~ is trusted as written, since the hook's shell expands it. Beside only stale hooks it runs orient, and its first stdout line names the settings file and why that hook cannot run. Done in c580568, with review fixes in dcbcef3 and the DEC-124 citation in 5e20dcf (lane wt/2026-10-30a-plugin: 5800cb9, 4da8788). AC-145 tested; DEC-124 PROVISIONAL. The kit README § Hook and FRAMEWORK's kit-block paragraph are updated.
