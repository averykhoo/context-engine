---
type: Decision
id: DEC-288
title: "CE-165: a guards receipt's not run counts only when it opens the receipt or is said of the gate in the same clause (INV-86), not the literal whole-receipt reading"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:f06b493a6e309a2bc443d34a92fa36c3194296ee4710a951309b6339731b4d2e
---

The agent's call on CE-165 (session 2026-11-07e), taking over INV-86's stricter match from DEC-162.

The owner-adopted advice (docs/evidence/owner-review-advice-2026-11-06b.md, via DEC-162) asks for "a stricter match (the whole receipt is "not run", or nothing)". Read literally, a whole-receipt match (`^\s*not run\s*$`) refuses the "not run, and why" form that the engine's own close remedy, manual-mode § session close and FRAMEWORK's receipts line ask for, and the receipts this repo's ledger already carries ("gate: not run (no code change); lint: clean", "no code changed; gate not run (records only, engine commits)").

So `not run` counts only when it opens the guards receipt or is said of the gate in the same clause:

    (?i)\d+ passed|passed \d+|^\s*not run\b|\bgate\b[^;,.]*?\bnot run\b

(config.py::GATE_RECEIPT and the kit's context.toml.template; this repo's context.toml adds its `|gate status`). "lint not run", "lint: clean; tests not run" and "gate green; lint not run" are refused; "not run: docs only", "the gate was not run (docs only)" and "1112 passed; lint not run" pass.

Rejected: the literal whole-receipt reading (above); "gate not run" only (refuses a bare leading "not run", the cli help's own example); a deny-list of "lint not run" and the like (open-ended).

Flag for the owner in the close digest: this narrows the owner-adopted wording. Cheap to undo: one regex in two places.
