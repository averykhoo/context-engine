---
type: Task
id: CE-181
title: '[gate] cannot hold a long multi-command gate, and banner set stales a gate whose scope holds HANDOFF.md'
pri: NOW
state: open
deps: []
goals: [G-6]
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-07e
updated: 2026-11-07e
---

[gate] cannot hold a long multi-command gate, and banner set stales a gate whose scope holds HANDOFF.md.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Found in CE-167: zanzibar's gate is ten commands, about 2.75 h, which [gate] cannot hold; and banner set rewrites HANDOFF.md, which zanzibar's code scope includes, so a close after a green gate stales it (worked around: close first, gate after). Idea: let the close receipt name a later gate run keyed by content id. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md § Engine findings
