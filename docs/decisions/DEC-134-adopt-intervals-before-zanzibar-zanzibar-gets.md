---
type: Decision
id: DEC-134
title: Adopt intervals before zanzibar; zanzibar gets its own task (CE-167)
actor: owner
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01a
body_sha: sha256:92868c46df9477bbc6fdfcb0a98929f4bc5ef6254d4835dca084508b2cc7ab8a
---

Owner, 2026-11-01a: *"Okay let's add Zanzibar as a task bit do intervals first"*

Context: the owner had said they wanted to migrate the zanzibar repo (graph-reachability-zanzibar-index) next, and asked whether that waited on feedback from audio-workspace. The agent answered that nothing on record waits on audio-workspace (CE-43 closed and pushed 2026-10-22), and that CE-11's recorded order puts intervals before zanzibar. So intervals is adopted before zanzibar, as CE-11 already orders, and zanzibar gets its own task, CE-167, which depends on CE-11.
