---
type: Decision
id: DEC-98
title: record confirm refuses a successor confirmed in the words that confirmed a story it supersedes; an exact repeat by the owner is quoted with when and where
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:ee23e25e17370e021f8f60ba5387d8060e51fbd0004973159c845d546d0459e7
---

The agent's call on CE-102, made while building it in session 2026-10-30a: how DEC-66 (a replaced reconstruction is re-confirmed by asking the owner again) is enforced.

Options:
(a) rule text only, no guard;
(b) `record confirm` refuses words identical (whitespace aside) to a `confirmed (by <who>): ...` amendment on any story down the successor's `supersedes` chain, with a remedy for an owner who genuinely repeats themselves: quote the words with when and where they were said;
(c) as (b), with an override flag.

Chose (b): it is the cheap guard the task suggested and it catches the copy-paste case DEC-66 forbids. Its false positive (the owner really says "yes" again) has a remedy that keeps the words verbatim inside a dated, sourced quote, without adding a flag an agent could reach for. Words matching an unrelated story's confirmation pass. Any added prefix gets past the guard, by design, since it targets copy-paste.

Known gap at landing (builder and reviewer, 2026-10-31): the refusal runs on the write only. G-I2 does not re-check a successor that someone confirmed by hand in a predecessor's words, so the by-hand path in manual-mode § context-engine record confirm has no lint backstop.

Built in lane commit 9ba1cf5, on main as 16bfb17 (AC-112). Cheap to undo: drop the check in working.py::Engine.confirm.
