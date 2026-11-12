---
type: Task
id: CE-230
title: Check mechanically that a build touching the framework's files was not done by a reading-tier builder (DEC-330)
pri: LATER
state: open
deps: []
goals: [G-7]
source: session 2026-11-12a
created: 2026-11-12
moved: 2026-11-12a
updated: 2026-11-12a
---

**Why:** DEC-330 puts a build that touches FRAMEWORK.md, the contract or the kit's runbooks on the most tier, but the rule lives only in prompts. The first task dispatched after it broke it: CE-218's work commit 801cb17 carries `Co-Authored-By: Claude Sonnet 5.5` and changes `docs/framework/FRAMEWORK.md` and two kit runbooks (the coordinator's workflow assigned the reading tier; the verifier passed the work). Found by the fable design review, `docs/evidence/fable-review-dec-328-336-2026-11-12.md` overall note 1, and confirmed first-hand with `git show 801cb17 --stat`.

**What:** a mechanical check, at `task close` or in housekeeping, that a task's work commits touching the framework's files (FRAMEWORK.md, `kit/contract.md`, `kit/docs/runbooks/`) were not co-authored by a reading-tier model. The trailers already carry the model (DEC-171). Sabotage: a fixture commit with a sonnet trailer touching FRAMEWORK.md must go red.

**Open:** whether it refuses or only warns, since a deliberate exception needs a way through.
