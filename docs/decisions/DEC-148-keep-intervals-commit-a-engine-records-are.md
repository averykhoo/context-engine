---
type: Decision
id: DEC-148
title: 'Keep intervals commit A: engine records are prose to gate.py and fuzz CI'
actor: owner asked
decided: 2026-11-03
session: 2026-11-03a
decision_status: PROVISIONAL
answers: ASK-27
ruled_by: claude-code/claude-opus-5-5
body_sha: sha256:5c72f967e7ed8f4998ab9c29c1beae23e0304f2a608ccb806a822325e7c48d3f
---

Owner, answering ASK-27 by delegating the ruling to claude-code/claude-opus-5-5: *"Yes finish the intervals migration and cutover"*

## Ruling

Ruled by claude-code/claude-opus-5-5 on the owner's delegation; only the quote above is the owner's words.

Keep commit A as it is (the question's recommendation). The owner asked to finish the cutover as built; commit A is part of that branch, its diff exempts only context.toml, docs/ledger/** and docs/archive/**, and its sabotage went red 5/5. PROVISIONAL: reverting it later is one intervals commit.
