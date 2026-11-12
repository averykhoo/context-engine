---
type: Decision
id: DEC-336
title: 'ask decide: what an owner-authored source is, no dead actor check, SUPERSEDED in the test fixture'
actor: agent (claude-sonnet-5-5)
decision_status: ACCEPTED
refs: [CE-218, US-24, DEC-325]
decided: 2026-11-11
session: 2026-11-11a
body_sha: sha256:f9ff7e32e7ce75f4d40f75fd44fdee90c84de5164e162d25a273b495d0e987fe
---

CE-218's builder pinned three details of `ask decide` that the plan and its addendum left open or got wrong against the code. The engine is a kit, so each is stated so that a repo with other kind names behaves the same.

1. **What counts as an owner-authored source.** A record whose `story_status` is `live` (FRAMEWORK §3.2), whatever its kind is called, since `[working]` has no story role; a decision whose `actor` is `owner` or `human:<id>` with no `ruled_by` (`decisions.py::owners_own`) and whose status is not SUPERSEDED or REJECTED; or a charter goal id (`guards.py::known_goals`). Anything else is only context: an agent's own earlier call never grounds a question.
2. **No owner-shaped check on the derived actor.** The addendum asked the op to assert that `agent (<model-id>)` is not owner-shaped. By construction it never is (`agent (...)` matches neither `owner`, `human:<id>` nor `owner asked`), so the check could not be made to fail and was left out; what keeps the decision off the owner is that a caller whose actor has no `/`, or starts `human:` or `process:`, is refused (`working.py::actor_model`), plus G-W4 on `agent_decided:`, which fails a decision whose actor is owner-shaped.
3. **The fixture's decision enum gains SUPERSEDED.** `tests/test_working.py::CONFIG` listed only PROVISIONAL, BUILT and ACCEPTED, so no test there could supersede a decision; the overturn path (`ask answer` superseding the agent's decision) needs it, as the repo's own `context.toml` already has it.

PROVISIONAL until the owner reviews it.
