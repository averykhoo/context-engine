---
type: Decision
id: DEC-138
title: 'CE-6 close-out scope: split hk.ratchet (CE-168) and ledger rotation (CE-169), drop adopt-and-close, build session touch and G-W11'
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:5ada733936a4fc031970f82f96764ffa2157c7a9cc58838f79b324fd7955a285
---

Agent's call, on the owner's "Finish ce6 now" (2026-11-01b): what finishing CE-6 covers.

- hk.ratchet is split out as CE-168: no G-V2 floor exists to ratchet (FRAMEWORK §8.5, deferred).
- Ledger rotation is split out as CE-169: no ledger cap is set, and §7.1 adopts rotation by trial (§11.4).
- Adopt-and-close is dropped as moot: a later conversation can already adopt a key and close it (store.py::Store._check_caller checks only the key's form; working.py::Engine._finalise checks only `kind: open`), and a dead conversation is covered by the derived digest (AC-167, DEC-69). One sentence in manual-mode § session abandon says so.
- `session touch` is built, per DEC-29's owner words ("If the session is still alive it should reset that number to zero or reset the last seen timer").
- G-W11 is un-deferred without a window measurement, since CE-7 closed without one. The window of 3 stays provisional. The hazard that it reds another session's gate is accepted, because it reports only the stubs DEC-69 already lets housekeeping abandon, and its remedy says to ask the owner first.
- CI checks out full history (US-18), so G-W9 and G-W11 check cited commits there as they do locally.
- G-W9 (and G-W11) go into config.py::LINT_IDS, so `[guards] off` and `coverage` can name them.

Each item is a record write or a local commit, cheap to undo; the owner can reverse any of them.
