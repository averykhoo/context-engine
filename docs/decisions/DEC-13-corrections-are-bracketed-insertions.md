---
type: Decision
id: DEC-13
title: "Corrections to append-only records are bracketed insertions; the typed words always survive"
actor: owner
decided: 2026-10-08
session: 2026-10-08c
decision_status: PROVISIONAL
tags: [records, append-only]
answers: ASK-2
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T19:00:00+08:00 }
body_sha: sha256:ad15d21e43a5a1a421efde73e2e15bff7b74a494d41a6fcdf521d308af765a65
---

Owner, answering ASK-2: *"What sort of correction does ask-2 cover? Just typos? Maybe you can
fix it in square brackets, but I think the goal is intent not bug for bug equivalence to what
the human typed. Verbatim quotes just preserves flavor and sometimes helps when we look back to
see if it might have been misread"*.

The agent's reading, recorded as the rule (FRAMEWORK §6.5, Q-I):

- ASK-2 asked about any change to the text above `## Amendments` in an append-only record
  (decisions, stories, deviations, ledger entries); the proposal was framed as typo fixes, but
  an unrestricted `correct` could change anything.
- `correct(id, after, text)` only **inserts** `[text]` after one unique anchor, re-stamps
  `body_sha`, and logs a `corrected:` line under Amendments. Removing the brackets it added
  gives back the original exactly, so a misreading can still be checked against what was typed.
- A change of meaning is an `amend`, never a correction.

PROVISIONAL until built and used in CE-5; the bracket form is the owner's suggestion ("maybe"),
and the insert-only check is the agent's way of keeping the typed words intact.

## Amendments

- **2026-10-10a (claude-code/claude-opus-5-5):** 2026-10-10 (DEC-22): the push clause is replaced. Ask before every push and push only on a green gate, CI or not.
