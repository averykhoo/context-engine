---
type: Decision
id: DEC-244
title: 'CE-188: HOLD is a fifth pri tier, last after SOMEDAY, on the task kind only, keyed on the literal name with no config key: rejected [working] hold key, SOMEDAY-as-hold or rename, a held flag/label, HOLD on the question kind (refs DEC-162)'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:4bddbfcb355bf7e71798112ff45e800d108f0e617c57aec9a84414b6d37580e6
refs: [DEC-162]
tasks: [CE-188]
code: [src/context_engine/working.py::HOLD]
---

Ruled at build time under DEC-162 (the owner filed the HOLD tier and left its shape to the agent, cheap to undo).

HOLD is a fifth `pri` tier, last after SOMEDAY, on the task kind only (context.toml and the kit's context.toml.template). The engine reads it by its literal name, through the constant `src/context_engine/working.py::HOLD`, as it already reads NOW, NEXT and SOMEDAY; there is no config key. A repo whose task enum lacks HOLD gets exactly the old behaviour.

Rejected:
- A `[working] hold` config key naming the held tier: tier names already carry engine meaning by their literal, and a key adds a schema field, its validation and an upgrade step nobody asked for.
- SOMEDAY as the held tier (the rerank skipping SOMEDAY), or renaming SOMEDAY to HOLD: SOMEDAY means "not this sprint" and must stay promotable by a rerank; a rename rewrites records and adopters' enums.
- A `held: true` field or a `held` label beside `pri`: either allows a held NOW item, which then needs its own guard, and a label the engine reads is magic. A tier is exclusive by construction.
- HOLD on the question kind: a question already waits on the owner, and an overdue question must still be raised.
