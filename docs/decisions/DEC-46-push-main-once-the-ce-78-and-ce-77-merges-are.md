---
type: Decision
id: DEC-46
title: Push main once the CE-78 and CE-77 merges are committed and both gates are green
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-15
session: 2026-10-15a
body_sha: sha256:7f3bcc1648aa9cd8c90c58f0449a3bc32186adfcadc0c63d24dc475182c4d148
---

Owner, 2026-10-15a, verbatim:

"If the repo looks good and it's in a working state, push after the commit"

Context: session 2026-10-15a was merging CE-78 and CE-77 into main (CE-64 and CE-81 already
merged and closed, both gates green). These words give push permission for main once those
merges are committed and the gate (Windows and Linux) is green; DEC-22 otherwise requires asking
before every push. Every push still gets a background CI watcher.
