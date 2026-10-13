---
type: Story
id: US-17
title: The framework runs from files it owns; CLAUDE.md carries only a bootloader pointer, and every agent role is defined in the framework
actor: owner
story_status: live
goals: [G4, G6, G7]
date: 2026-10-13
body_sha: sha256:9ca7fa497fdcb9fc276a1e73f7db851880233c1858e60ecb52b80d5d13d4d0ee
---

Owner, 2026-10-13a, on whether the "top level coordinates" rule (DEC-16, FRAMEWORK §6.6) should go into the global ~/.claude/CLAUDE.md so it applies in repos that have not adopted the framework:

"It shouldn't be in Claude md, it should be in the framework, since this framework when adopted shouldn't depend on the user not making changes to Claude md. It does need to hook into Claude md but it should be like a short pointer out like a bootloader, then we can run the framework without too much changing in Claude md? At least that's what I was thinking, any better ideas?

Also the coordinator agent should be defined or included in some list of agents? Iirc we also use scout or explorer agents, those should be somewhere in here, although the agent description might currently be in some global config maybe, but that should be copied into here. Unless we only use Claude default or built in agents in which case nvm"
