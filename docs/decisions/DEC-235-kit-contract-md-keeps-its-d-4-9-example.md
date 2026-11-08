---
type: Decision
id: DEC-235
title: 'kit/contract.md keeps its D-4..9 example: changing contract text reds G-D0 in every adopted repo until it upgrades'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:e05200f929ad3b2ca77b74c4f39e68666a56f7436ce7b8f5e82b9ca2aca038a9
---

For CE-56: kit/contract.md names `D-4..9` as its example range for `decision accept`, which is the old kit's decision prefix.

The call: kit/contract.md keeps its `D-4..9` example. Lint G-D0 compares it byte for byte with every adopted repo's copy, so changing its text reds every adopted repo until it upgrades; and a contract change needs a framework version bump. `DEC-4..9` would also be a hit for tests/test_kit.py::LEAK. The example stays until the next framework version changes the contract for another reason.

Options:
(a) leave it: chosen;
(b) change it now: rejected, for the reasons above.

Cost to undo: cheap (nothing changed).
