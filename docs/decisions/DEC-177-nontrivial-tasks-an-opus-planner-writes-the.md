---
type: Decision
id: DEC-177
title: 'Nontrivial tasks: an opus planner writes the design, a sonnet builder executes, an opus verifier checks'
actor: owner
decided: 2026-11-07
session: 2026-11-07d
decision_status: ACCEPTED
body_sha: sha256:1884145ce88ac98ab1380ddae9ec0b65e1f0ea138848e00613cdebb2984c68c2
---

Owner, 2026-11-07d:

> i think that for any nontrivial task, an opus agent should write or at least see the plan, but sonnet can probably be the one to execute it - does that seem correct? or is sonnet smart enough to plan complicated things on its own?

The agent's reply proposed this shape (quoted, the agent's words):

> for any task above DEC-173's size floor, an opus planner reads the code and writes a short design. That covers the behaviour, the rejected options, and the edge cases as concrete test inputs, because the test cases are where the design actually lives. Then a sonnet builder executes and an opus verifier checks. Below the floor, there's no planner. This also widens the trial: tasks like CE-158 would qualify once the planner settles their design, rather than going straight to opus.

> If you agree, I'd record your words as a decision that amends DEC-173's trial shape, update CE-198, and add the planner step to the workflow. CE-161 is already running on the current shape, so it would be the last task run without a planner, and CE-191 would be the first with one.

Owner, 2026-11-07d:

> okay
