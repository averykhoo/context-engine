---
type: Task
id: CE-85
title: "Kit README names the MCP connect timeout: the server took 33-36 s to start under load against Claude Code's 30 s limit; MCP_TIMEOUT is the remedy"
brief: "From CE-77's review, 2026-10-15a. A kit edit: the CE-7 freeze applies"
pri: LATER
state: open
deps: []
source: session 2026-10-15a
created: 2026-10-15
moved: 2026-10-15a
updated: 2026-10-20e
goals: [G-4]
---

CE-77 review (session 2026-10-15a): the MCP server's start took 33-36 s under load, past Claude Code's 30 s connect limit. Setting MCP_TIMEOUT is the remedy and the kit README does not mention it. Also from the same review (LOW): the plugin launcher stays quiet when any settings hook's command mentions context_engine ... orient, including a stale one with another machine's path in a committed .claude/settings.json, which then fails silently.
