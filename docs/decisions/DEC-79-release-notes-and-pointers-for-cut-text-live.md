---
type: Decision
id: DEC-79
title: Release notes and pointers for cut text live outside FRAMEWORK.md, since AC-33 keeps ids out of it
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:7b27767d41a255a4a1d5b14d809bea143f8ea274d90c462462ea8be2da661ec1
---

An agent's call under P8 (cheap to undo), made by CE-93's builder in session 2026-10-23f and landed in c5b812f. Recorded afterwards from the builder's report. This one decision carries two calls (the builder's PROVISIONAL calls P-2 and P-5), because both follow from the same constraint.

**Calls.**
1. Release notes live in a new `docs/framework/RELEASE-NOTES.md`, not in FRAMEWORK.md. FRAMEWORK §6.12 and §8.0's upgrade procedure point at it. Its baseline is the rules changed since `FRAMEWORK-v0.5.md` (2026-10-10), taken from the `git log` of FRAMEWORK.md; a task id is cited where no decision was recorded.
2. FRAMEWORK.md's pointers for cut text go to the archived copy, `RELEASE-NOTES.md` and `docs/engine.md`, not to decision ids. Incident ids wait for CE-94 (DEC-47).

**Why.** AC-33 (`tests/test_kit.py::test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths`) forbids CE, DEC, US, AC and INV ids in FRAMEWORK.md, while CE-93 asked for release notes by decision id and for a decision-id pointer for each cut. Both can only be met outside FRAMEWORK.md.

Task: CE-93. Commit: c5b812f.
