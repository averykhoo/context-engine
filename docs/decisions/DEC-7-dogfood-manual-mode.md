---
type: Decision
id: DEC-7
title: This repo uses the framework now, by hand, in the v0.5 record shapes
actor: owner asked
decided: 2026-10-08
session: 2026-10-08a
decision_status: BUILT
tags: [dogfood]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
body_sha: sha256:382a3cf5eed713d9a2d39cd58116a14a128c29ca606a153060a6eb1f1909f9fb
---

Owner: *"use the context engine framework for the context engine repo"*. Until the engine
exists, this repo runs the framework in **manual mode**:

- records are hand-written OKF files in the v0.5 shapes, so they become the engine's first
  real fixtures: tasks and owner questions in `tasks/` (board size 2, one file per item),
  decisions in `docs/decisions/`, stories in `docs/stories/`, the ledger in
  `docs/ledger/session-log.md`;
- id prefixes, chosen because each had zero occurrences in the repo on 2026-10-08 (the
  FRAMEWORK text cites other repos' `D-n`, `S-n`, `T0`-`T3`, `Q-A`-`Q-K`): tasks `CE-n`,
  decisions `DEC-n`, stories `US-n`, criteria `AC-n`, owner questions `ASK-n`;
- frontmatter that the engine will own is hand-maintained until then; `body_sha` is omitted and
  will be stamped when the engine adopts the records (CE-8);
- the guards do not exist yet; the rituals are followed by hand from `CLAUDE.md`.

Story status uses `story_status`, task state uses `state`, decision status uses
`decision_status`, because OKF reserves `status` (FRAMEWORK §9.3.1).

## Amendments
