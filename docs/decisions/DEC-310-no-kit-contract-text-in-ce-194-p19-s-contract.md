---
type: Decision
id: DEC-310
title: "No kit contract text in CE-194: P19's contract line waits for the next contract version bump (CE-207), since editing kit/contract.md now turns G-D0 red downstream"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:52d39f20907d5b5ec1a7491536e06c358190250d5ffd170dc04b723d481095b8
---

**Decision:** CE-194 changes no kit contract text. P19's contract line waits for the next contract version bump, filed as CE-207, a LATER task shaped like CE-132. Suggested line for the contract's Gate section: "A green gate is the whole release decision (FRAMEWORK P19): a check only a human runs is a board item to automate, never an accepted residual."

**Why:** CE-132 is closed and 0.6's contract bump is done. Changing `src/context_engine/kit/contract.md` now, without a version bump, turns G-D0 red in every adopting repo on the editable install, since their `docs/framework/contract.md` no longer matches the installed kit's. FRAMEWORK §1 carries the principle meanwhile, which every session can read.

**Rejected:** editing the kit contract now (a second 0.6 contract change; G-D0 red downstream).
