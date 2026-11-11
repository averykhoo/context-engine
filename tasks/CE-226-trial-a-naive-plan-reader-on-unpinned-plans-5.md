---
type: Task
id: CE-226
title: Trial a naive plan reader on unpinned plans (5 plans)
pri: NEXT
state: open
deps: []
goals: [G-1]
source: session 2026-11-10c
created: 2026-11-10
moved: 2026-11-10c
updated: 2026-11-11a
---

Trial a naive plan reader (DEC-327, idea 3). Elephant-goldfish's comprehension reviewer sees the document alone; a builder is effectively such a reader.

- On plans that do not pin the design, a sonnet agent reads only the plan and lists every unstated assumption, undefined term or step it could not carry out. The planner then revises.
- Trial: 5 plans. Compare what it found with the defects the verifier later found on the same tasks, and record the cost (about $0.2-0.5 per plan, estimated).
- Adopt it only if it catches defects the verifier would have caught at a fix round's cost.

## Log

- 2026-11-11a (claude-code/claude-sonnet-5-5): CE-218 (2026-11-11, plan pinned, written 2026-11-10): naive reader raised 41 itemized findings in 4 kinds (16 undefined terms, 11 steps it could not carry out, 7 unstated assumptions, 7 contradictions/tensions); the planner's addendum grouped them into 8 verdicts: 4 wholly REAL-GAP (signature/check order/body layout, close matching/overturn/reopen, runbook/ops/cli/test content), 1 wholly ALREADY-COVERED (helper locations), 1 wholly NOT-A-PROBLEM (contradictions; only the file count was wrong), and 2 mixed (stub/receipt/G-W4 terms: covered in code but the decided: line format a REAL-GAP; assumptions: CE-217 hand-over, 'already put' test and unblocking REAL-GAP, jargon NOT-A-PROBLEM). Of the verifier's defects across rounds (1 round, 1 defect: CE-218 not built because CE-219 holds NOW and CE-217 is uncommitted, against a dispatch premise that CE-217 was committed): a REAL-GAP finding anticipated the CE-217-uncommitted half (naive 'Line 55: CE-217 is already built before CE-218 starts' assumption, pinned in addendum I as 'CE-218 starts only after CE-217 is committed'); it missed the CE-219-holds-NOW half (G-W5 one-NOW rule) and the fact that the dispatch, not the plan, was wrong. Naive-reader cost not visible in the files.
- 2026-11-11a (claude-code/claude-sonnet-5-5): CE-217 (2026-11-11, plan pinned, written 2026-11-10): naive reader raised 17 findings (6 unstated-assumption, 5 step-not-executable, 3 undefined-term, 3 contradiction); the planner's addendum grouped them into 13 verdicts and judged 11 REAL-GAP, 0 already covered, 1 NOT-A-PROBLEM (the sizing terms, for the coordinator not the builder), and 1 split (item 13: not a problem in substance, a real gap in wording). Of the verifier's defects across rounds: none to match, because the build never ran. The builder stopped before any change (CE-219 holds NOW), the verifier's round-1 PASS covers only that conduct and found 0 defects in plan or addendum, so 0 defects were anticipated by a REAL-GAP finding and 0 missed. The Linux gate could not run (WSL DNS timeout). Naive-reader cost: not visible in the files.
