---
type: Decision
id: DEC-88
title: "A decision text holding ## Amendments is refused at the write, through G-I3's shared check"
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:67aea9742cfd83ee0b76e418d1a150ac91864fa1ebc71451afbbef2e8332e1c6
---

`guards.py::delegation_problems(new=True)`, called by `record new` and `ask answer`, refuses a
`## Amendments` line anywhere in the text being recorded (owner words or ruling, delegated or
not), and its remedy names `record amend`. At rest the line belongs to the amendments, so G-I3
lint names a hand-written one under "Not checked" (FRAMEWORK §8.1, manual-mode § context-engine
lint).

Options weighed:
- (a) A write-time refusal through G-I3's shared check: chosen, the narrowest fix the CE-138
  brief asks for.
- (b) Only a "Not checked" line: rejected, it leaves text below the line outside `body_sha`
  with nothing to stop it.
- (c) A general refusal in `store.new` for every append-only kind, stories included: rejected
  for now, wider than the brief.

Cost: `[guards] off = ["G-I3"]` also turns off the Amendments refusal, which is a body_sha
integrity check; neither FRAMEWORK §8.1 nor manual-mode says so yet. Stories keep the gap: `record
new story` with a `## Amendments` line in its body creates a story whose text below that line is
outside `body_sha` (follow-up task).

Landed in the CE-138 commit (lane commit de6d55e, integrated on main as 9700437).
