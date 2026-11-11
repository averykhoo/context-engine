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
updated: 2026-11-11a
---

Trial settled findings in fix rounds (DEC-327, idea 1 of docs/evidence/elephant-goldfish-model-vs-our-review-2026-11-10.md).

- The fix-round prompts carry a settled-findings ledger. The builder answers each verifier defect with FIX, CONTEST or ESCALATE:
  - CONTEST must cite evidence the verifier could read.
  - ESCALATE goes to the coordinator, when only knowledge outside the files refutes the defect.
- A settled finding is not reopened in a later round.
- Add a stop signal: when a new finding would revert an earlier fix, stop and escalate, on top of the 3-round cap.
- Trial on the next wave. Record per task: rounds, findings reopened, contests upheld.
- If adopted, write it into docs/runbooks/fan-out.md and its kit copy (byte-equal, LF).

## Log

- 2026-11-11a (claude-code/claude-sonnet-5-5): CE-218: fix rounds 1; contests 0, upheld 0; settled findings reopened: 0; stop signal: fired; escalations: 1 (fixer-r1 ESCALATE on the single defect, CE-218 not built: needs CE-217 built and committed, then NOW moved off CE-219, then re-dispatch). The ESCALATE answer is the one that changed what happened: FIX would have meant inventing CE-217's FRAMEWORK 5.3/6.5 and procedures wording and promoting past CE-219, so nothing was written; the verdict stayed FAIL with no deliverable, and the Linux gate was not run (docker registry unreachable, infra).
- 2026-11-11a (claude-code/claude-sonnet-5-5): CE-217: fix rounds 0; contests 0, upheld 0; settled findings reopened: 0; stop signal: not fired; escalations: 0 (no fixer-r* files exist, and the verifier's one round, verifier-r1, found nothing to fix because CE-217 was not built: the builder stopped on CE-219 holding NOW and the closer held the close). The FIX/CONTEST/ESCALATE answers did not change what happened: none was exercised, so this trial yields no evidence on them.
- 2026-11-11a (claude-code/claude-sonnet-5-5): CE-219: fix rounds 0 (the verifier passed in round 1, no fixer-r*.md exists); contests 0, upheld 2; settled findings reopened: 0; stop signal: not fired; escalations: 0 (no `escalated:` comment needed). The FIX/CONTEST/ESCALATE answers changed nothing, since no FAIL occurred and none of them was exercised; the verifier's only items were 3 non-blocking residuals.
- 2026-11-11a (claude-code/claude-opus-5-5): the CE-217 and CE-218 rows above are void: a coordinator script bug ran their builds before CE-219's (the lock followed plan-finish order), so both builders stopped on the NOW conflict and nothing was built; the re-run's rows replace them.
- 2026-11-11a (claude-code/claude-sonnet-5-5): CE-217 (re-run, replaces the void row): fix rounds 0; contests 0, upheld 0; settled findings reopened: 0; stop signal: not fired; escalations: 0. The verifier's one round (verifier-r1) passed with no blocking defect, no fixer-r*.md exists, and its 6 non-blocking items went to the closer as residuals INV-252 to INV-257 (INV-257 is the owed trial record). The FIX/CONTEST/ESCALATE answers did not change what happened: none was exercised, so this row gives no evidence on them.
