---
type: Decision
id: DEC-316
title: 'CE-193 pick-up 2026-11-08: entry 3 done, no task; 5 and 10 one task; 11 a bug; CE-193 stays open'
tasks: [CE-193]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:f3a7856c0e298ba6fb3bda3a7803623c2a2c86cd77359dc6b464f21170d45dcf
---

An agent's call under P8 (cheap to undo: records only, a local commit), made by CE-193's builder in session 2026-11-07e on 2026-11-08, following the planner's design for picking up audio-workspace's `docs/context-engine-feedback.md` entries 1 to 12. Not owner words.

1. **Entry 3 gets no task.** It is built by CE-44, CE-158 and CE-201: guards.py::ask_problems refuses a question with no context, fewer than two options, or an empty, placeholder-only or unreasoned Recommendation; working.py::Engine.ask_new calls it, and G-W4 rechecks open questions in lint. audio-workspace needs only a re-pin.
2. **Entries 5 and 10 are one task (CE-209).** Both change working.py::Engine.ask_answer, and coupled work goes to one agent.
3. **Entry 11 is filed as a bug (CE-211)** in working.py::Engine.commit's call to gate.py::check_commit, which counts paths an op line names, against check_commit's docstring; not as self-committing board writes, which DEC-36 rules out as the default and `[engine] commit = "every-write"` (config.py::COMMIT_POLICIES) already offers per repo.
4. **Entry 9 is filed (CE-210) though mostly met:** the kit's fan-out.md already has the on-return check; only its claim that a write-capable agent can always persist changes.
5. **CE-193 stays open as the standing pick-up.** Its Log records entries 1 to 12 taken and 13 as the next.
6. **The questions for entries 8 (ASK-37) and 12 (ASK-38) are filed at LATER**, following ASK-33's precedent. Entry 12's words are audio-workspace's record of owner words (its D-413) and are not recorded here as owner words until the owner answers ASK-38.
7. **A read bug found while doing this is filed (CE-212):** working.py::Engine.show replaces every `PLACEHOLDER` in a body when it splices the shown Log, so `task show CE-193` printed its item 3 corrupted. Not from the feedback file; filed so it is not lost.
8. **The planner's trap for entry 4 was corrected in CE-208:** guards.py::_ask_label opens a part at any heading, so only a heading deeper than the part above it (not any unknown `##` heading) is read as Recommendation text. Probed at cb362ca.
