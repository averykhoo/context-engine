---
type: Decision
id: DEC-198
title: 'CE-170 bullet 3 (test the dry branch of Engine._hk_reindex) dropped: the method was removed by CE-185 (7a19c83)'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:57a1c4b8594c12b01dc788adf40e48b64ccb843b694b41f19ff87b0bd6c4db26
---

CE-170's third bullet (test the dry branch of working.py::Engine._hk_reindex) is dropped, not done: the method was removed by CE-185 (7a19c83), and `git grep _hk_reindex HEAD -- src tests` finds nothing, so there is no branch left to test. CE-170.
