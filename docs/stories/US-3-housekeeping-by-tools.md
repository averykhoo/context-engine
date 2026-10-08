---
type: Story
id: US-3
title: Housekeeping at session start or before close, by tool-using agents
actor: owner
via: Claude Code chat session 2026-10-08a
date: 2026-10-08
story_status: live
goals: [G3]
---

## Owner's words (verbatim)

> i feel like there should be a housekeeping run at session start or just before close, using
> smaller subagents that can use tools so they don't manually break things - tools like the task
> tool, esp for simple things like marking tasks as done or adding timestamps or appending
> comments

## Notes

AGENT: landed as FRAMEWORK §6.11. "Marking tasks as done" is the one judgement call in the list:
housekeeping closes only on recorded evidence (a verified `Closes:` trailer or a ledger line),
otherwise it proposes the close (G-W9). Amended by DEC-4: a script or MCP first, before edit
subagents.
