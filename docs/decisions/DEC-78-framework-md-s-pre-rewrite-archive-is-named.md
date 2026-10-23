---
type: Decision
id: DEC-78
title: FRAMEWORK.md's pre-rewrite archive is named FRAMEWORK-v0.5-2026-10-23.md
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:ba592efa95549a8e2e35a442f68786fbb175b1eb117b45ff226c1f2bd5c2bcd7
---

An agent's call under P8 (cheap to undo), made by CE-93's builder in session 2026-10-23f and landed in c5b812f. Recorded afterwards from the builder's report (its PROVISIONAL call P-1). Not owner words.

**Call.** The copy of FRAMEWORK.md archived before CE-93's rewrite is named `docs/framework/FRAMEWORK-v0.5-2026-10-23.md`: a byte copy of FRAMEWORK.md at 6871040 under an `ARCHIVED` first line.

**Why.** `FRAMEWORK-v0.5.md` already exists (the 2026-10-10 copy, frozen), and the framework version cannot move to 0.6 without an engine version bump, because G-D0 ties the contract's `framework:` to the engine's major.minor. A dated name avoids both. It still matches the frozen-provenance route pattern `FRAMEWORK-v0.*.md`.

Task: CE-93. Commit: c5b812f.
