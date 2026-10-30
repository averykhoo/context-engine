---
type: Decision
id: DEC-90
title: G-I3's blind spot gets a register entry
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:c225f342165d4bc39258b20dcd0937ec376d206e5a71036c6aef1790ad62b1b5
---

G-I3's blind spot, a ruling made on the owner's delegation but recorded with neither `ruled_by`
nor a `## Ruling` section, gets an entry in the residual-risk register. DEC-27 only fixes the
INV-n prefix; FRAMEWORK §7.4 (P17's register of risks left after their controls) calls for an
entry, because this risk is controlled only at the individual rung.

Options weighed:
- File an entry through CE-139's design review: chosen.
- Record why no entry is needed: rejected, an individual-rung residual is exactly what the
  register holds.

Filed by `task close CE-139`, which reads the `- residual:` line in its Design review section.
