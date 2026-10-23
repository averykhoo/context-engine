---
type: Decision
id: DEC-77
title: Delegated-ruling provenance applies going forward; a frozen record is fixed by recording again and superseding
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:8b55041d49fe9b67c6a40b54900e9a7be9cff8998418cdf196a0e03fd4bdb926
---

An agent's call under P8 (cheap to undo), made by CE-113's builder in session 2026-10-23f and landed in 21a88d9. Recorded afterwards from the builder's report (its PROVISIONAL call 9). Not owner words, and not a ruling on the owner's delegation.

**Call.** The delegated-ruling rules apply going forward only: no existing record is rewritten. No operation corrects a frozen record's provenance (`decision set` refuses `actor` and `ruled_by`); the remedy for a delegated ruling stamped as the owner's is to record it again in the new shape and `decision supersede` the old one, which is what G-I3's remedy text names.

**Why.** No record in this repo has `ruled_by` or a delegated ruling stamped as the owner's (the decisions that prompted CE-113 are another repo's), so there is nothing to migrate here. Provenance is frozen by design; a supersede keeps the history readable instead of editing it.

Task: CE-113. Commit: 21a88d9.
