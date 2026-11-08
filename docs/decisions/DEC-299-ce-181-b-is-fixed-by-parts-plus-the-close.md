---
type: Decision
id: DEC-299
title: CE-181 (b) is fixed by parts plus the close procedure (gate run --stale, then gate status --require <scope>+parts), not by a close receipt naming a later run (circular, unverifiable) nor by excluding HANDOFF.md automatically (fail-open)
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:647f2507af829e19443d886bb44e67f535de9e9347cdba93105e28dc0c813c28
---

CE-181 (b), a close's banner write staling a gate whose scope holds HANDOFF.md, is fixed by parts
and the close procedure, with no change to `session close` or `banner set`: the close's writes
stale only the parts keyed on a scope holding them (zanzibar: the lean phase, about 100 s, not the
nine pytest tiles), and step 7 runs `gate run --stale`, then `gate status --require
<scope>+parts`.

Rejected: (1) a close receipt naming a later gate run by content id, the item's idea. The receipt
sits in the ledger, inside the `all` id it would name (circular); the run ledger is gitignored,
so no reader of tracked state can verify it; and it lets a close certify a run that has not
happened. (2) Excluding HANDOFF.md, or every engine-written file, from scope ids automatically:
fail-open, since zanzibar's lean phase lints HANDOFF.md and a banner can turn it red; an exclusion
stays the adopter's, under a guard. (3) A warning from `banner set` or the close: it would hash
the tree on every banner write, and `gate status` already says it.
