---
type: Decision
id: DEC-186
title: Derive OKF status in the Store, not an Engine op (CE-179)
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:a4b96ea296417381a230f03e2b9a4da7db26b219ef6fceb38c5ec768a1325b7a
---

Store.create_many and Store.new give a board item created with `state: closed` the OKF `status: deprecated` (FRAMEWORK §9.3), instead of an Engine op doing it. The bulk caller seen (the zanzibar CE-167 helper) calls Store.create_many directly, and no task-import op exists yet (CE-174, CE-178), so an Engine-level fix would miss it.
