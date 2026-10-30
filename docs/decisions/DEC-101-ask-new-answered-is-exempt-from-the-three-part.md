---
type: Decision
id: DEC-101
title: ask new --answered is exempt from the three-part question body check
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:79fea4debbad809bcad254fd551a54b47e4d084381787cecfdab832b3c2b4519
---

The agent's call on CE-111, made while building it in session 2026-10-30a: `ask new --answered` is exempt from CE-44's three-part question body check.

Options:
(a) exempt it: the question was asked and answered in chat, and the decision holds the answer; its default body says so;
(b) require context, options and a reasoned recommendation in its body too.

Chose (a): the parts exist to help the owner answer, and the owner has already answered. G-W4 reads only open questions, and an answered question is filed closed.

Built in lane commit 530bc18, on main as 3247ca7; documented in manual-mode § ask new. Cheap to undo: run the CE-44 check in working.py::Engine.ask_answered.
