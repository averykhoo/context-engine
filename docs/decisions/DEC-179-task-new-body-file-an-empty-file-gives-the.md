---
type: Decision
id: DEC-179
title: 'task new --body-file: an empty file gives the default body'
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:7ac996ef463cee02c78d75a9322e7b691bde8f8dfc2d555c90c1abbb3e1c99a5
---

task new --body-file with an empty file gives the default body: an empty or whitespace-only file means no body, exactly as --body "" does (Engine.new's body.strip() test). A refusal was rejected as stricter than --body.
