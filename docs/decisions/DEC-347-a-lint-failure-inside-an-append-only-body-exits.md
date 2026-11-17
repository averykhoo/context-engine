---
type: Decision
id: DEC-347
title: A lint failure inside an append-only body exits through a per-record waiver, not grandfathering
actor: claude-code/claude-opus-5-5
decided: 2026-11-17
session: 2026-11-17b
decision_status: PROVISIONAL
body_sha: sha256:0344f919a2e80feb6114dbfcda1126b13c845e55028b51ce17199658779b37da
tasks: [CE-239, CE-238, CE-240, CE-241]
---

An agent's call under P8 (cheap to undo: a record write), ruled by the coordinator of session 2026-11-17b after the engine-feedback collation, its independent verification and fable's second opinion. Not owner words; PROVISIONAL until the owner reviews it.

**Problem.** Lint runs G-D3 at rest over append-only bodies (decision and story text above `## Amendments`), which an adopter may not edit, and the engine offers no recorded way out of a red there. Two adopters hit it on the way to 0.6 (docs/evidence/engine-feedback-2026-11-17.md, items F31 and F32):
- adhoc-microphone-array: its story prefix is one letter, so the formula `(M-4)(S-3) >= 6` in two of its decisions reads as citations of story ids that do not exist (F32).
- audio-workspace: 137 `<id> § <n>` citations fail; 131 clear once G-D3 counts bold-numbered paragraphs and top-level ordered items as sections (F31's task), but 6 cite a section the target really lacks, all inside append-only decision bodies (F31's residual).
`record correct` only inserts text; superseding a decision to silence lint, or turning G-D3 off for the repo, both misstate the record. Every future guard that reads bodies will land on frozen text the same way (imports, bodies written before the guard).

**Call.** A lint failure inside an append-only body exits through a per-record waiver, not grandfathering. A record op (working name `record waive <id> <guard> "<exact text>" --reason "<why>"`) appends an amendment in the shape the `corrected:` entries already use, naming the guard, the exact text and the reason. Lint reads that entry and skips that exact text, for that guard, in that record only. It never waives a whole guard for a record, never covers text appended after the waiver (a later amendment repeating the text is red again), and the entry is op-owned and checked like `corrected:`, so a hand edit is caught. It is a record write: an agent may make it, and the close digest flags it. Every citation is then either resolvable or explicitly, visibly signed off.

**Rejected.**
- A math- or context-aware heuristic in the id matcher: fragile, special-cases one formula, and would hide a real citation such as `(see S-3)`.
- Grandfathering by `body_sha` or by a date baseline: it hides exactly what the at-rest check exists to find in old bodies (audio-workspace's 6 real mis-citations would vanish), the baseline is arbitrary, and it amounts to turning the guard off by stealth.
- A per-repo `[guards] allow_ids` list: one line of code, but repo-wide and permanent, so a genuinely mistyped id anywhere later passes. Kept only as an emergency fallback if the op slips.

**Basis.** docs/evidence/engine-feedback-2026-11-17.md (items F31, F32 and § Second opinion, which summarises fable's recommendation of exactly this mechanism and the rejected options above).
