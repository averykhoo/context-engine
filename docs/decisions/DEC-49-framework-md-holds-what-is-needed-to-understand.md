---
type: Decision
id: DEC-49
title: FRAMEWORK.md holds what is needed to understand and use the framework, not its history
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-15
session: 2026-10-15c
body_sha: sha256:97da6fe64a5eed1d27004a49c4df850b6a4e7c6f50443e6747b346fd6c4f7dd7
---

Owner, 2026-10-15c, verbatim:

"okay with dedupe-1 and dedupe-2, and framework.md also needs cleaning up after archiving the current version. framework.md should include the framework but not necessarily the full history of where all the ideas came from. it should be what's needed to understand and use the framework, not what's needed to be a historian."

Context (AGENT): dedupe-1 and dedupe-2 are from a redundancy review in session 2026-10-15c.
- dedupe-1: clean close runs the full gate at step 2 and again at step 7 ("Lint and `<gate>` again", procedures.md § Clean close), though only records change between them and the gate already runs lint. Step 7 becomes `gate status --require code` plus lint (G-V1), not a second full test run.
- dedupe-2: FRAMEWORK.md carries build status (*Not built yet (CE-n)*, *Built so far*) throughout, although §8.0.3 says what is built is on the board, not there; each marker goes stale (CE-89 is that upkeep). Build status leaves the spec.
"Archiving the current version" is §6.12's step: copy FRAMEWORK.md to FRAMEWORK-v<version>.md, opened ARCHIVED <date>, before the rewrite.
