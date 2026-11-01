---
type: Decision
id: DEC-146
title: 'CE-6 close: coverage reading G-W10 as built goes to CE-164; the close clause is narrowed'
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:d82f7c5af16ea930d5a807d159d405ecccaaf5799c5223dd565449a5f3896e45
---

Agent's call (2026-11-01b), on the final verifier's HOLD for CE-6. The planner's close definition required `coverage` to read G-W9, G-W10 and G-W11 as built. On main at ee44e68, G-W9 and G-W11 read built. G-W10 reads deferred. The reason is that the frozen coverage map `docs/evidence/framework-coverage-2026-10-12.md` marks it DEFERRED ("Un-defer: CE-6 or CE-12 runs real housekeeping"), and guards.py::_item_status calls a G-id built only when it is in config.LINT_IDS. G-W10 is a count in `hk run`'s reply, not a lint guard, so it can never pass that test as worded.

Ruling: the clause is narrowed to "G-W9 and G-W11 read built; G-W10 is built as `hk run`'s count line (AC-177) and its tests are green". Making coverage read it as built is left to CE-164, whose title is exactly this gap ("housekeeping parts G-D12 does not extract, and a frozen map outranking the board").

Options weighed: (a) write a new full dated coverage map now: refused, because it would duplicate CE-164's work and pre-empt its design; (b) hold CE-6 open: refused, because the work is built, verified and green on Windows and Linux; (c) narrow the clause and hand the reading to CE-164 (chosen). It is cheap to undo: one record and one comment.
