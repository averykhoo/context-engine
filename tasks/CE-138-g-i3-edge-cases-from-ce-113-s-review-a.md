---
type: Task
id: CE-138
title: "G-I3 edge cases from CE-113's review: a capitalised Owner passes, a ruling may hold ## Amendments, AC-53 omits ruled_by"
brief: Each gap gets a refusal seen to fail (DEC-11) or a Not checked line in 8.1; AC-53's text must name ruled_by
pri: LATER
state: open
deps: []
goals: [G-2]
source: session 2026-10-23f
created: 2026-10-24
moved: 2026-10-23f
updated: 2026-10-23f
---

G-I3 edge cases and AC-53's text, from CE-113's review

Three non-blocking findings of CE-113's verifier (verify-1, Non-blocking 1 to 3), on 21a88d9. Filed in session 2026-10-23f.

1. `docs/criteria.md` AC-53's provenance list omits `ruled_by`, though AC-53's test (its parametrize row in `tests/test_decisions.py`) now has a `ruled_by` row, and AC-99 states the refusal. Text drift only.
2. `guards.py::delegation_problems` matches case-sensitively: `actor: Owner` or `ruled_by: Owner` passes both the write-time refusal and G-I3. Low risk: no actor vocabulary uses capitals.
3. A ruling whose text holds a `## Amendments` line is accepted: the text below that line falls outside `body_sha` and reads as an amendment (the builder flagged this too).

For 2 and 3: refuse it (one check shared by `record new`, `ask answer` and G-I3; sabotage it red first, DEC-11), or name it under G-I3's "Not checked:" in FRAMEWORK §8.1.

## Traps

- AC-53 is a criterion: changing its text may need a recorded call (P14), even though it only catches up with its test.
- The verifier's edge probes were pure-function calls to `guards.py::delegation_problems`; a fix must also hold through `record new` and `ask answer`.

## Read first

- `.scratch/ce-113/verify-1.md` (CE-113's verifier report, Non-blocking 1 to 3; gitignored, so the findings are restated above)
- `guards.py::delegation_problems`; FRAMEWORK §8.1 G-I3; `docs/criteria.md` AC-53 and AC-99
- DEC-73 to DEC-77 (CE-113's design calls)

## Log
