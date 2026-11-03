---
type: Task
id: CE-174
title: task new has no --body-file
brief: ask new has one; multi-line bodies need it
pri: LATER
state: open
deps: []
goals: [G-1]
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-02a
updated: 2026-11-03b
---

task new takes --body only, while ask new takes --body or --body-file. Found in CE-11 (2026-11-02a).

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Hit again in CE-167: a 181 KB task body cannot fit a Windows command line; worked around by calling Store.create_many through the pinned env. A task import op would also serve CE-178/CE-179. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md § Engine findings
