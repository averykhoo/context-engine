---
type: Story
id: US-4
title: The MCP server is local, per repo, started and stopped with each session
actor: owner
via: Claude Code chat session 2026-10-08a
date: 2026-10-08
story_status: live
goals: [G4]
body_sha: sha256:63ba55d793a0563e73310193b758d037d9e0218a89acff8acc3013b82bd199ee
---

## Owner's words (verbatim)

> can an mcp server be a local thing? ideally i don't need to spin up a server myself, can this be
> done per-repo within sessions and shut down at the end? is that a bit too much though

## Notes

AGENT: answered yes (stdio, from a committed `.mcp.json`); verified by the step-0 spike
(`spike/FINDINGS.md`): variable expansion, subagent sharing, and shutdown at session end.
