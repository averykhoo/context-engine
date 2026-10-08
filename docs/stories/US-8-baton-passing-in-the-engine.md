---
type: Story
id: US-8
title: The engine handles baton passing
actor: owner
via: Claude Code chat session 2026-10-08a
date: 2026-10-08
story_status: live
goals: [G3]
body_sha: sha256:74562a3b4ae1bcf0a0466ad4a24b70dc5b8f9defaccb55096af350435f4daf28
---

## Owner's words (verbatim)

> help sketch out what the mcp should do for us. does it also do the ephemeral baton passing bit?

## Notes

AGENT: answered yes: batons and pause blocks become records the engine owns (FRAMEWORK §5.4);
they are tracked and committed, and they expire, rather than being ephemeral.
