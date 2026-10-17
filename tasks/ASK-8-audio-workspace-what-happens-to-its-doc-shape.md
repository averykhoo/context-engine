---
type: Question
id: ASK-8
title: 'audio-workspace: what happens to its doc-shape tests (claudeMdShape, handoffShape, decisionsIndex) in the migration?'
brief: 'Rec: retire handoffShape+decisionsIndex, rewrite claudeMdShape; keep docLinks, architecture, runbook'
pri: NEXT
state: open
deps: []
source: session 2026-10-17b
created: 2026-10-17
moved: 2026-10-17b
updated: 2026-10-17b
last_asked: 2026-10-17b
blocks: [CE-43]
---

Seven tests in audio-workspace src/__tests__ guard doc shape. Three collide with the migration: claudeMdShape (CLAUDE.md under 40,000 bytes, authority-table rows under 600 bytes, must point at the decision log's index), handoffShape (HANDOFF.md under 4000 lines, keeps '## WHAT IS LEFT' and the '### Recent round records' divider) and decisionsIndex (docs/decisions.md carries a generated, fresh index; no D-n cited without a definition). The engine's lint and orient cover these jobs once the board, banner and decisions are records. docLinks (relative links resolve), architectureShape (ARCHITECTURE.md a map under 16 KB) and runbookShape (testing-runbook under 2000 lines, dated baselines) do not collide and still guard something the engine does not.
