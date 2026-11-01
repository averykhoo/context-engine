---
type: Decision
id: DEC-140
title: G-W11 skips only when git says the clone is shallow; a repo without git is still checked
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:500aef2b2ae42fcd6fbb5d2153a8b00ce721136edf48362fb66678c30878a4da
---

The agent's call on CE-6, made while building G-W11 in session 2026-11-01b: when G-W11 skips its check because git history may be missing.

Options:
(a) skip unless `git rev-parse --is-shallow-repository` says `false` (the plan's wording), so a directory git cannot read is skipped too;
(b) skip only when `git rev-parse --is-shallow-repository` says `true`.

Chose (b): a repo with no git at all is still checked, because staleness then reads only the op log, which is exact. Only a shallow clone lacks commits that would count against a stub, so only it is skipped.

Built in lane commit 06c925a, on main as 9bdb909; pinned by AC-173 (test_g_w11_reports_nothing_in_a_shallow_clone). Cheap to undo: one condition in working.py::Engine._stale_stub_failures.
