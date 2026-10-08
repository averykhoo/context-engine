---
type: Decision
id: DEC-9
title: No SQLite or other database as the source of truth
actor: owner
decided: 2026-10-08
session: 2026-10-08a
decision_status: REJECTED
tags: [storage]
reopen_if: plain-file queries become too slow on a real corpus; even then only as a derived, disposable index
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
body_sha: sha256:bc64c881d48803385e8ad59d374fec2924615f0a31ec23c11567eb20d6ecfabb
---

Owner: *"i guess it could also be sqlite but thats not as friendly to human readers/editors or
git"*. Records stay plain OKF markdown in git. A database may exist only as a derived,
disposable index (FRAMEWORK §0.2, §9.4).

## Amendments
