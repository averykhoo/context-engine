---
type: Decision
id: DEC-116
title: Criterion writes are not milestones
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:fff966fb9180fa67051af6c10fff3ca91a386d3d1d3605d84bb5c432f5b3e045
tasks: [CE-42]
code: [src/context_engine/working.py::Engine.criterion_new]
refs: [DEC-36]
---

CE-42's `criterion new` and `criterion set` are not milestones: they ride along with the next commit, as `doc.freeze` and `doc.archive` do.

Options: (a) ride along like `doc.freeze` and `doc.archive`; (b) make them milestones. Picked (a): DEC-36's milestones are owner words, hand-offs and closes, and a criterion is drafted by the agent. The design reviewer (.scratch/2026-10-30a/build/crit-design-review.md) agreed.

Code: working.py::Engine.criterion_new, working.py::Engine.criterion_set; tested by tests/test_commit.py::test_the_milestones_are_dec_36s_and_every_other_write_rides_along.
