---
type: Decision
id: DEC-144
title: An hk run phase skips hk stamp when no question kind is configured; its commit takes the batch's title
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:ba787a98d411d163c1294446438742e58448ec90daed8e4e1b6cf283676cb7a0
---

The agent's call on CE-6, made while building `hk run` in session 2026-11-01b: what a phase does when no question kind is configured, and what its commit is titled.

Options:
(a) a phase runs `hk stamp` regardless and refuses when no question kind is configured; the commit gets a fixed `hk run` title;
(b) a phase skips `hk stamp` when no question kind is configured; the commit title is whatever the batch would give it (`engine: <ops>`, or a close's title).

Chose (b): a repo without questions has nothing to stamp, so refusing would block every run there; and reusing the batch's title keeps one title rule for every engine commit.

Built in lane commit 8e0f5e3, on main as 3ae496a; pinned by AC-175. Cheap to undo: working.py::Engine._hk_steps and the batch title.
