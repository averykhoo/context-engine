---
type: Decision
id: DEC-142
title: 'Single-item hk comment needs no Session: line; the scan lists untrailered id-led commits as foreign and skips closed ids silently'
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:c843d7542e8821f359c6e9d2ee6391c9a29ef879e0020d986052d32526eb98d3
---

The agent's call on CE-6, made while building `hk comment` in session 2026-11-01b: which commits single-item `hk comment` and the scan accept, and what the scan says about the rest.

Options:
(a) both forms require a `Session:` trailer on the commit, and the scan stays silent about commits without one;
(b) single-item `hk comment` does not require a `Session:` line, since the caller names the commit; the scan lists as `foreign: reconcile` every commit with no trailer whose title leads with an existing id, and skips without a line the ids that name closed items or questions.

Chose (b): a caller naming a commit has already judged it, and a scan that lists untrailered id-led commits points at the foreign commits that procedures § Reconciling foreign commits must handle, instead of hiding them. Closed items and questions take no comment, so a line for each would be noise.

Built in lane commit 3230363, on main as 92c56bc; pinned by AC-174. Cheap to undo: the plan's filters in working.py::Engine.hk_comment_plan.
