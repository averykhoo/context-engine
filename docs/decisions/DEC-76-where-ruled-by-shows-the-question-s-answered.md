---
type: Decision
id: DEC-76
title: "Where ruled_by shows: the question's answered mapping, the log line, the decision index, the kit contract and the schema"
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:ca298f339200596d0c1ea58a05896bc28fd728761b5406a85c5dd5038246d6b6
---

An agent's call under P8 (cheap to undo), made by CE-113's builder in session 2026-10-23f and landed in 21a88d9. Recorded afterwards from the builder's report. This one decision carries four small calls (the builder's PROVISIONAL calls 5 to 8): each only decides where `ruled_by` is shown or declared, so they are one piece.

**Calls.**
1. `ask answer` also writes `ruled_by` into the question's `answered:` mapping, and its log line and reply say "answered on the owner's delegation, ruled by X".
2. The decision index line gains `ruled by X`, only for records that have it; existing index lines are unchanged.
3. The kit contract gains one sentence under "Who decides" (copied byte-equal to `docs/framework/contract.md`).
4. `ruled_by = "str"` is declared in `[kinds.decision]` types, in this repo's `context.toml` and in the kit's `context.toml.template`.

**Why.** Whoever reads a question, the decision index or the log should see that the answer was delegated without opening the record; the contract is where sessions learn who decides; and the schema declaration lets lint type-check the field.

Task: CE-113. Commit: 21a88d9.
