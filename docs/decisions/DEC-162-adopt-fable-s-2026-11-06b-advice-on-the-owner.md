---
type: Decision
id: DEC-162
title: Adopt fable's 2026-11-06b advice on the owner review queue
actor: owner asked
ruled_by: claude-code/fable
decision_status: PROVISIONAL
decided: 2026-11-06
session: 2026-11-06c
body_sha: sha256:cfe95efccceea6c0bfaec879557095093f76e743324f1851668dc60563c60a9d
refs: [DEC-97, DEC-110, DEC-120]
amends: [DEC-107]
---

okay take fables recs, and push when the gate is green

## Ruling

The recommendations a fable agent gave on 2026-11-06b, frozen as `docs/evidence/owner-review-advice-2026-11-06b.md` (commit 962b4b3), are adopted as written there, each item with the one word that doc ends it in. In short:

- PROVISIONAL is split: decisions whose actor is the owner are born ACCEPTED; agent calls stay PROVISIONAL until a new op, `decision accept <ids>` (ranges allowed), marks them reviewed. A NOW task builds it. The listed agent calls (DEC-86..90, 92..96, 98..106, 108..109, 111..119, 121..130, 133, 148..149, 159..160) are accepted through that op once it exists, not by hand before.
- DEC-97: text is enough (no named-agent install). DEC-107: gate_receipt on by default in the engine. DEC-110: `--residual` stays optional. DEC-120: cut OKF `log.md` and `generated.by`.
- DEC-125 supersedes DEC-88; DEC-126 and DEC-112 are linked. No merges.
- Tasks to file: a HOLD tier (LATER); a louder close that warns when NOW is empty (NEXT, a warning not a refusal); two mechanical conflict checks, duplicate live titles and a relates/narrows link kind (LATER); a lighter shape for one-off permissions (LATER).
- Board: CE-156 and CE-158 to NEXT; CE-153 merged into CE-154; CE-159 merged into CE-156; CE-162 dropped; CE-163 becomes a register entry and closes; CE-157 waits on the next release; CE-165 lists its tests and takes INV-86's stricter match; CE-47 to NEXT; CE-56's rename half declined; CE-132 waits on the PROVISIONAL task; CE-28 to LATER; CE-40 takes the gap.
- Register: INV-89 and INV-90 merged into one entry; INV-97 retired as a duplicate of INV-95.
