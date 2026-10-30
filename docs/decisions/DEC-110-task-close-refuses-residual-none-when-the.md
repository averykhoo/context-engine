---
type: Decision
id: DEC-110
title: task close refuses --residual none when the design review lists a residual, and its Log names every INV id the close files
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:c8a03ff701163198a333add3533cfe0f0a229672a21940a550326975fb49fd61
---

The agent's call on CE-120, made while fixing its review findings in session 2026-10-30a: what `task close --residual none` does on an item whose design review lists a residual, and what the close's Log line names.

Options:
(a) only log the filed ids even when `none` was said, so the Log silently overrides the stated answer;
(b) refuse the `none` (the same way `none` plus a stated risk is already refused) AND log every filed id, the review's included, plus `already in the register: <ids>` on a re-close;
(c) refuse only.

Chose (b): a stated 'none' that is false is the entry-33 confusion, so refusing it teaches the closer; logging the ids makes the Log true for reviewed closes made without `--residual` too, and the re-close line is no longer empty.

Built in lane commit 73da625, on main as 8fe039d (working.py::Engine.close, working.py::Engine._filed_before); pinned by AC-127. Cheap to undo.
