---
type: Decision
id: DEC-120
title: 'OKF profile (FRAMEWORK §9.3): build the stale_after refusal and the charter_status read; cut the generated log.md and generated.by'
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
tasks: [CE-136]
code: [src/context_engine/guards.py::stale, src/context_engine/guards.py::charter_problems, src/context_engine/working.py::Engine.unconfirmed_charter]
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:802fef8d2a5d87ea1eecbd798ee46906301159ff2d1fafe7a8dd088630f3eee0
---

Each of the four parts FRAMEWORK §9.3 claimed but nothing built is decided one way or the other (CE-136).

1. Concept changelog `log.md`. Options: generate `docs/decisions/log.md` from creates/amends/retires on every decision write, with a G-D6-style regeneration check, or cut it. CUT. OKF does not require a `log.md`. The op log already records what changed when, per write, and the decision index covers the decisions. Only 2 of the roughly 115 decisions carry any of creates/amends/retires (both are amends of another DEC), so the file would be nearly empty, yet it would cost the same plumbing as the decision index: a render, a write hook, commit's derived map, hk regen, a lint check and a by-hand fallback. Reopen if a census or trace-check that reads creates/amends/retires is built, or if a consumer reads OKF `log.md`.

2. `generated.by`. Options: stamp `generated: {by, at}` on every record at creation, or cut it. CUT. The op log carries the writing agent on every write, and a second copy in frontmatter could disagree with it. A hand-written `generated` (the charter has one) is round-tripped like any unknown key. Reopen if an OKF consumer outside the engine needs who-generated in the file itself.

3. `stale_after`. BUILT as G-D4's freshness half (guards.py::stale). An expired `stale_after` on a live item is red, and so is a value that is not an absolute instant. It reads live records, the criteria table's optional `stale_after` column and register entries' `- **stale_after:**` line. G-D4 was chosen rather than a new G-id because the check is P2 liveness (is it kept current?) and because a new G-id would turn G-D12 red until a coverage map or board item names it. Option rejected: a new G-id, or extending G-W3.

4. `charter_status`. BUILT. G-I1 checks the vocabulary (`confirmed`, `unconfirmed` per §11.4) and that the charter's OKF `status` holds none of our states. Orient asks the owner about an unconfirmed charter. Option rejected: a lint failure on an unconfirmed charter, rejected because a migrated repo legitimately starts unconfirmed.

Code: guards.py::stale, guards.py::charter_problems, working.py::Engine.unconfirmed_charter.
