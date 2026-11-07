---
type: Decision
id: DEC-209
title: 'The check runs before the write, not as lint before the milestone commit (CE-183): a refused commit would still leave a stamped red record'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:19648322190dc4adcc4b4323974d1e2364c9fb4c95ea0f8d0bd2f9e6dd296c88
---

The citation check runs on the new text before it is written, not as a lint before the milestone's auto-commit (the item's first option). By the time a milestone would commit, the record is already written and stamped, so a refused commit leaves the same unfixable record, only uncommitted. A whole lint per milestone is also slow, and it would block a milestone on any unrelated red in a path the milestone carries.
