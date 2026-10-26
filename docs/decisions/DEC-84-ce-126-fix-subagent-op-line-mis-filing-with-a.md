---
type: Decision
id: DEC-84
title: 'CE-126: fix subagent op-line mis-filing with a lane field (option B), kept at LATER'
actor: owner
decided: 2026-10-26
session: 2026-10-26c
decision_status: PROVISIONAL
answers: ASK-21
body_sha: sha256:ab29db984bd5e9a94ea30a4cd4572a7e308aafb398dc891345b31820f7400476
---

Owner, answering ASK-21: *"Owner, 2026-10-26c, answering a multiple-choice question in chat.

Question: "ASK-21 / CE-126: subagents run under the coordinator's session key, so `commit` can't tell whose op lines are whose (e.g. 8291569 'CE-133' carried baton.done BTN-5). So far nothing has been lost; lines only got filed under the wrong task. Which fix, and when?"

Selected: "B, later (Recommended)": "Add a lane field on each op line (CE_AGENT / --agent / MCP `agent` = task id); commit selects by session+lane; close takes all lanes. Additive, no migration, fits one-subagent-one-task-one-commit (DEC-60). Keep CE-126 at LATER, since the harm so far is mis-filing only.""*
