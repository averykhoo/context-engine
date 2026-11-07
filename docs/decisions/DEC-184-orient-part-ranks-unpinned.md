---
type: Decision
id: DEC-184
title: Orient part ranks unpinned
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:b0057997fa22d7379eb7e2f89c3e9abf701d4b0bcfe06ef6eea8c1d15716e966
---

Each orient part's byte rank ("its bytes come with parts ...") and its cut pointer (the command naming the rest) is described in manual-mode § context-engine orient, but no test pins them against `working.py::Engine.orient`'s `rank=` and rest arguments. This is a residual: a part whose rank changes in code can leave the runbook's rank prose stale, and nothing goes red.

Rejected: pinning the ranks against the prose, which couples a test to free wording for a small docs item.

Made for CE-200.
