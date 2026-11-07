---
type: Decision
id: DEC-183
title: Conditional orient parts as continuations
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:aec83638272f97b1cbd0324f4ce918dfb6cd2a507891a39d9b951fc99770c6d8
---

In manual-mode § context-engine orient, each conditional orient part is described as a "then, only when ..." continuation of the numbered part it follows in the output, as part 3 already did for `Follows`, `Continues` and `Last close` and part 4 for `Rerank due`. The numbers 0 to 7 stay, so the paragraph saying which parts' bytes come first is unchanged.

Rejected: renumbering every part (22 numbers), which would rewrite the byte-order paragraph and every "part N" reference for no gain.

Made for CE-200.
