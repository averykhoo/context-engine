---
type: Decision
id: DEC-73
title: "A delegated ruling keeps the owner's words above a ## Ruling section and names who ruled in ruled_by"
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:5d34901897989d50547e985fc75c2af3b7ed664a8f19f8ac331b1b40e1b82418
---

An agent's call under P8 (cheap to undo), made by CE-113's builder in session 2026-10-23f and landed in 21a88d9. Recorded afterwards from the builder's report (its PROVISIONAL calls 1 and 3). Not owner words, and not a ruling on the owner's delegation.

**Call.** A ruling made on the owner's delegation is a decision whose body holds the owner's delegating words, then a `## Ruling` section holding the ruling, and whose frontmatter names who ruled in `ruled_by`. `ruled_by` may name an agent or another human (`human:<id>`); only `owner` and a blank value are refused.

**Why.** The owner's delegating words stay in the stamped body (covered by `body_sha`, G-D10), so they are frozen as owner words, while the ruling below them is visibly someone else's. The alternative, a separate `delegation:` frontmatter field holding the quote, would move owner words out of the stamped body. The owner may delegate to another person, so `ruled_by` refuses only the values that would make the ruling read as the owner's own.

Task: CE-113. Commit: 21a88d9.
