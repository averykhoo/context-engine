---
type: Decision
id: DEC-301
title: With gate parts, the scope guard keys on the running part's scope (CE_GATE_PART), not on [gate] require
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:324c243348dd1d096006a79d7c2e0e2baaae7a6349e76289e1a6161b895df163
---

**Decision:** with `[gate.parts]`, `gate run` runs each part's command with `CE_GATE_PART` set to the part's name (`gate.py::PART_ENV`; a single-command run clears an inherited one), and `scope_guard.py::_install` keys the guard on that part's `scope` instead of `[gate] require`. Run outside `gate run` (no `CE_GATE_PART`), the guard keys on `require` as before, and its verdict says so and names `gate run --part <name>`. With parts declared, the guard's remedy is a part keyed on a scope that holds the path, never `readers` (parts take none). A scope that excludes nothing has nothing for the guard to see, so it notes no process either.

**Why:** a part is fresh on its own scope's id (DEC on part coverage), so what its tests may read is exactly that scope. Keying on `require` is wrong both ways: a part keyed on every file whose tests read HANDOFF.md fails with a remedy (`readers`) that `gate.py::_parts` refuses (the CE-181 r1 verifier's repro), and a part keyed on the code under a wider `require` could read records unseen while its freshness ignores them (fail-open). An environment variable is the one channel a part's command inherits on every platform without the adopter editing the argv.

**Rejected:** the union or intersection of the part's scope and `require` (the union is fail-open for a narrow part; the intersection re-creates the verifier's failure); a flag appended to the part's argv (not every part's command is pytest); turning the guard off for wide parts (loses the narrow-part check).
