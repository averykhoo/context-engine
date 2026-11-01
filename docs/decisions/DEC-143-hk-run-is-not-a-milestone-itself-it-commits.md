---
type: Decision
id: DEC-143
title: hk run is not a milestone itself; it commits once at its end only when one of its writes is a milestone
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:2186309f1234ad48aecc9a7d78f7df5aba3133ec8a1d40d36dd6bad50056d2ec
---

The agent's call on CE-6, made while building `hk run` in session 2026-11-01b: whether `hk run` is a milestone (DEC-36).

Options:
(a) `hk run` is a milestone and always commits at its end;
(b) `hk run` is not a milestone itself: it runs in one batch and commits once at its end only when one of its writes is a milestone (an abandon, now wrapped in store.milestone(), or a close); otherwise its writes go with the session's next commit.

Chose (b): DEC-36 commits at milestones, not at every write, and a run whose only writes are stamps or comments is not one. tests/test_commit.py::test_the_milestones_are_dec_36s_and_every_other_write_rides_along holds the list.

Built in lane commits 8e0f5e3 and b17d1d9, on main as 3ae496a and b16384a; pinned by AC-175. Cheap to undo: the milestone wrapping.
