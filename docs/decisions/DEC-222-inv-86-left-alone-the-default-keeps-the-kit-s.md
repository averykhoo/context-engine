---
type: Decision
id: DEC-222
title: "INV-86 left alone: the default keeps the kit's loose 'not run' match; tightening it is CE-165's job"
tasks: [CE-192]
refs: [INV-86]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:effe6eb44878f7fa7f2eb8418a5e90948c00a523b79496b7c6584de0473f9854
---

The agent's call on CE-192: the engine's default keeps the kit pattern as it is, its loose `not run` alternative included.

INV-86 records that a receipt passes on the words `not run` anywhere in it (e.g. `lint not run`) with no gate result. Tightening the pattern changes what the default means and is its own task, CE-165; CE-192 only moves the existing kit value into the engine, so it is left alone here.

Cost to undo: cheap.
