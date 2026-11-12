---
type: Task
id: CE-225
title: 'Build a plan-citation check: every path and file::symbol a plan cites exists before the build'
pri: NOW
state: open
deps: []
goals: [G-1]
source: session 2026-11-10c
created: 2026-11-10
moved: 2026-11-12a
updated: 2026-11-12b
---

Build a plan-citation check (DEC-327, idea 2): before a builder starts, every `file::symbol` and path a plan cites is checked to exist. Elephant-goldfish's codebase_details reviewer does this with an agent; here it should be mechanical.

- A read-only engine verb or tool that takes a plan file and lists the cited paths and symbols that do not exist, using the same resolution as the existing `file::symbol` citation checks (find them first; G-D3 checks citations in records).
- The wave workflow runs it after the planner and sends a plan with dead citations back to the planner.
- Sabotage: a plan citing a missing symbol must be refused.

## Log

- 2026-11-12b (claude-code/claude-opus-5-5): 99801e1: CE-225: promote to NOW (DEC-337)
