---
type: Decision
id: DEC-300
title: gate status, not orient, reports stale parts (hashing the tree at every SessionStart costs every session); FRAMEWORK §8.5 G-V1 amended to say so
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:c49cef912887e82443176a22054770c81b15481a7fe69019f17a8eded463e738
---

`gate status`, not orient, reports the stale parts. FRAMEWORK §8.5 G-V1 said a long suite's parts
would be split "with `orient()` reporting the untested parts"; orient runs from the SessionStart
hook at every start, resume and compaction and is byte-capped, so hashing the tree there would
cost every session, including those that never touch the gate. The spec is amended in place
(DEC-19) to name `gate status` as the reporter.
