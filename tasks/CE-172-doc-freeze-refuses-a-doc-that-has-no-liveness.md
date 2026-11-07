---
type: Task
id: CE-172
title: doc freeze refuses a doc that has no liveness line
brief: Hit in CE-43 and again in CE-11; both froze by hand
pri: NOW
state: closed
deps: []
goals: [G-6]
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-07e
updated: 2026-11-07e
status: deprecated
closed: 2026-11-07e
---

doc freeze refuses a doc with no liveness line, so an adopter freezing an imported decision log writes the FROZEN line by hand. Seen in CE-43 (audio-workspace, 2026-10-19d) and CE-11 (intervals docs/decisions.md, 2026-11-02a).

## Log

- 2026-11-03b (claude-code/claude-opus-5-5): Reproduced again in CE-167 (all three zanzibar runs, on docs/architecture/decision-log.md); FROZEN line written by hand per manual-mode. Evidence: docs/evidence/ce167-zanzibar-cutover-2026-11-03.md § Engine findings
- 2026-11-07e (claude-code/claude-sonnet-5-5): closed: doc freeze writes the FROZEN line into a doc that declares no liveness (after the H1, else after frontmatter, else line 1); verifier PASS
  residual risk: INV-143, INV-144, INV-145
