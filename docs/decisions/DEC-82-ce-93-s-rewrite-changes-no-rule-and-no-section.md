---
type: Decision
id: DEC-82
title: CE-93's rewrite changes no rule and no section number; DEC-50's trap-lifetime rule waits for CE-29
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:fc2e5540d35627992d5115cbd50ea3d0d0ed98fbf508005266dba7a0cb2d7792
tasks: [CE-93]
---

An agent's call under P8 (cheap to undo), made by CE-93's builder in session 2026-10-23f and landed in c5b812f. Recorded afterwards from the builder's report. This one decision carries two calls (the builder's PROVISIONAL calls P-6 and P-7), both on the scope of the rewrite.

**Calls.**
1. DEC-50's trap-lifetime rule was not written into FRAMEWORK.md: it is CE-29's change, not this rewrite's.
2. No section was removed or renumbered: section numbers, §6's item numbers and §6.6's verbatim paragraphs are unchanged.

**Why.** CE-93 cuts the text to what a user needs and changes no rule; adding a rule would break the release notes' "No rule changed". Section and item numbers are cited by `docs/runbooks/procedures.md` and the tests (AC-36, AC-33's §6.6 paragraphs, §7.5's runbook names), so keeping them avoids churn in every citer.

Task: CE-93. Commit: c5b812f.
