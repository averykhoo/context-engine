---
type: Decision
id: DEC-307
title: P19 is a new numbered principle at the end of FRAMEWORK §1, pointed at from P7, §3.3 and §7.4, not an insert that renumbers P8..P18 nor a P7 clause (US-20, P3)
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:39f2c8e55389ed27a8eee0583793f6ae17f92ad08cd49e3732f8756312550e23
---

**Decision:** US-20's principle is a new numbered principle, P19, at the end of FRAMEWORK §1. P7, §3.3 and §7.4 point at it with "(P19)".

**Why:** P3 forbids renumbering, and principles are cited by number: `src/context_engine/review.py` cites P17 and P18, and the contract cites P7 and P8. So "beside P7" is met by a pointer bullet in P7, not by placing the principle there. The owner asked for "a framework principle" (US-20), and a clause inside P7 cannot be cited on its own. P7 is also about guards, not about what decides a release.

**Rejected:**
- inserting after P7 and renumbering P8..P18 (P3);
- P19 out of numeric order right after P7 (a reader scanning for P8 meets P19, and the order test would need a special case);
- a P7 sub-bullet only (not a principle);
- `P7a` (a new id shape nothing parses).

**Pinned by:** `tests/test_principles.py::test_the_principles_run_from_p1_with_no_gap_or_repeat_and_keep_their_numbers` and `tests/test_principles.py::test_p7_section_3_3_and_section_7_4_point_at_p19` (CE-194, AC-184).
