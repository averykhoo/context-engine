---
type: Task
id: CE-179
title: 'G-W4: a bulk import does not derive status: deprecated from state: closed'
pri: NOW
state: open
deps: []
goals: [G-6]
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-07e
updated: 2026-11-07e
---

G-W4: a bulk import does not derive status: deprecated from state: closed.

## Traps

- none yet

## Read first

- none yet

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Found in CE-167 (first-hand): G-W4 wants status: deprecated on every closed item, but Store.create_many does not derive it from state: closed (249 lines). Fix: derive the OKF status at import. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md § Engine findings
