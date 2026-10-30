---
type: Decision
id: DEC-100
title: An answered question skips the tier cap
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:9773d305c2c6feb87ae8a02ed1bfd028bdfbe070793b7b171dff2a46ce1e268c
---

The agent's call on CE-111, made while building it in session 2026-10-30a: an answered question skips the tier cap.

Options:
(a) `ask new --answered` files its question with `Engine.new(capped=False)`, skipping the tier cap;
(b) apply the cap as every other `new` does.

Chose (a): the question is closed before the commit and never holds a place in its tier, so under (b) a full NEXT would refuse recording an owner's answer.

Built in lane commit 530bc18, on main as 3247ca7; pinned by AC-120 (working.py::Engine.ask_answered, working.py::Engine.new). Cheap to undo: drop `capped=False`.
