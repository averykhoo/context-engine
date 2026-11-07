---
type: Decision
id: DEC-131
title: 'CE-110: owner pastes shell rules 1 and 2; rule 3 only if ulimit -u is shown to work in Git Bash'
actor: owner
decided: 2026-11-01
session: 2026-10-31a
decision_status: ACCEPTED
answers: ASK-22
body_sha: sha256:db5068c1dfa2fb35d7e4bd907de683b8c89c98645e37c2d790ecb491383afdc4
---

Owner, answering ASK-22: *"Owner's answer, 2026-11-01. They picked an option in a chat question; the option text is quoted verbatim:

"Paste 1+2, test 3 (Recommended)": "You paste rules 1 and 2 into ~/.claude/CLAUDE.md (1 in the narrower wording, 2 labelled 'suspected'). An agent checks whether ulimit -u does anything in Git Bash; rule 3 goes in only if it works. Then close CE-110."

Context the owner saw before choosing: .scratch/asks-22-23/context.md and fable.md (2026-10-31). Rule 1 in the narrower wording is "never `bash <file>` a path held in a variable without checking its extension". Rule 2 is "never background an && chain", labelled "suspected cause, not proven"."*
