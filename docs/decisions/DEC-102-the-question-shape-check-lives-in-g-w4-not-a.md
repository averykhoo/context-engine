---
type: Decision
id: DEC-102
title: The question-shape check lives in G-W4, not a new guard id
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:9cf96903768748e6d5e30c93e382bfd74c67684ea21a0b6c13987ea4f3af97ab
---

The agent's call on CE-44, made while building it in session 2026-10-30a: the lint half of DEC-34's rule (a question carries context, options and a recommendation) lives in G-W4, not a new guard id.

Options:
(a) G-W4, which already checks the board's questions (no open question carries `answered:`);
(b) a new G-W14 that can be switched off on its own.

Chose (a): FRAMEWORK naming a new G-id turns G-D12 red until a board item names it, and board writes were the integrator's, so the worktree gate could not be green. Cost: a repo cannot switch the question-shape check off without losing G-W4's state checks.

Built in lane commit 143bb4b, on main as 10f8717; pinned by AC-121 and AC-122. Cheap to undo: rename the failure id, then `task comment` a board item naming it.
