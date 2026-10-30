---
type: Decision
id: DEC-93
title: AC-33 drops its allowance for (CE-n) build marks in FRAMEWORK.md
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:e3885e8cff08d0820e9ccc15f1e7a3174181ba1572dc16bb4aa837b77d48a1e9
---

The agent's call on CE-143, made while building it in session 2026-10-30a (P14: a criterion change).

Options:
(a) drop AC-33's allowance for `(CE-n)` build marks in FRAMEWORK.md, so FRAMEWORK.md is leak-checked like every kit file;
(b) keep the allowance in case build marks come back.

Chose (a). DEC-81 removed every build mark and the Summary paragraph that explained them, so the allowance only lets a stray mark back in unseen. AC-33's text now reads "neither the kit nor FRAMEWORK carries this repo's ids (a `(CE-n)` build mark included: DEC-81) or paths". The test change removed tests/test_kit.py::BOARD_MARK and leaks()'s `allow_marks` parameter; tools/sabotage_ce26.py follows the new signature.

The criterion text changed in the build commit before this decision was recorded, because builders do not write records; the integrator records it with the close.

Built in lane commit 78ab6af, on main as e13f852. Cheap to undo: restore the allowance and the AC-33 wording.
