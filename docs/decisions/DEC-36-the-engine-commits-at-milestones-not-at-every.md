---
type: Decision
id: DEC-36
title: The engine commits at milestones, not at every write; CE-55 builds it
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-13
session: 2026-10-13c
body_sha: sha256:4469e609c2cd9e560cd625bafc3592bf4e7df3fa11d14613df0a1c9f4a649f22
---

Owner, 2026-10-13c, after CE-45 landed (every engine write commits itself), asked:

"do we really need to commit at every write? every task completion yes, but what other scenarios make a commit worthwhile?"

The agent's recommendation it answers (2026-10-13c): keep CE-45's sweep machinery (`commit.py::commit`), change its trigger. `[engine] commit` becomes a policy: `milestones` (the default), `every-write`, `off`. Milestones are task close (carrying `Closes:` and the sabotage lines), the owner-words writes (story new, amend and retire, decision, ask answer), pause and baton, and session close. Task new, comment, set, section, touch, ask raised and session start ride along with the next commit. A `context-engine commit <paths> -m ...` wraps `git commit -o` with the sweep, so the session's own commits never split records from their op lines. Folded into CE-55, after CE-49 merges.

Owner's answer:

"Your recommendation seems fine, yup file and bump it to next"
