---
type: Task
id: CE-224
title: Trial settled findings (FIX/CONTEST/ESCALATE) and a revert stop signal in fix rounds
pri: NEXT
state: open
deps: []
goals: [G-1]
source: session 2026-11-10c
created: 2026-11-10
moved: 2026-11-10c
updated: 2026-11-10c
---

Trial settled findings in fix rounds (DEC-327, idea 1 of docs/evidence/elephant-goldfish-model-vs-our-review-2026-11-10.md).

- The fix-round prompts carry a settled-findings ledger. The builder answers each verifier defect with FIX, CONTEST or ESCALATE:
  - CONTEST must cite evidence the verifier could read.
  - ESCALATE goes to the coordinator, when only knowledge outside the files refutes the defect.
- A settled finding is not reopened in a later round.
- Add a stop signal: when a new finding would revert an earlier fix, stop and escalate, on top of the 3-round cap.
- Trial on the next wave. Record per task: rounds, findings reopened, contests upheld.
- If adopted, write it into docs/runbooks/fan-out.md and its kit copy (byte-equal, LF).
