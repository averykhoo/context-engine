---
type: Decision
id: DEC-188
title: 'Scope of the status derivation: literal state closed on board kinds only (CE-179)'
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:5f875e405893f094488aa642f18ba23a231e74a2d3e9281e41d56fcfaab6efe9
---

Scope of the derivation: only the literal `state: closed` on `[working] board` kinds maps to `status: deprecated`. A null or blank `status` counts as absent. Kinds off the board (decision, story, baton, pause) and other states (done, expired) are untouched, matching G-W4's scope.
