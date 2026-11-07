---
type: Decision
id: DEC-178
title: "CE-191: session close warns of an empty NOW on its reply's first line, from the board it leaves"
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-07
session: 2026-11-07d
body_sha: sha256:c3db650a018a964e3bf0f286d851bb6e30b0ceca726f9574e47196aae56d08d9
---

The planner's call on CE-191's open shape (DEC-162 fixed only "a warning, not a refusal"). Cheap to undo: one reply clause and two runbook paragraphs.

- **Where the warning goes: the close's reply, at the end of its first line, as `; WARNING: <the CE-36 text>; say so in the owner digest`.** Not written into the ledger entry. Rejected: an extra summary line (breaks the 1-to-7-line digest cap the close itself enforces); an engine-written `Still owed:` line (puts words the closer did not give into an owner-facing record, and the extra text meets `_refuse_prose`'s ledger checks, so the warning could turn into a refusal, which DEC-162 rules out); a line of its own (AC-19: a write's text is one line, and an MCP close without housekeeping output is one line today). The next session still sees an empty NOW without a ledger line: orient prints `no NOW item`, and lint fails G-W5 with the same remedy.
- **When it fires: the board as the close leaves it, whoever emptied NOW.** It is computed after close housekeeping (`hk run close` can close the NOW item itself). Unlike CE-36's `_now_left`, it does not ask whether this op took the item off NOW: a close hands the board to the next session, so an empty NOW is the close's to report, whoever emptied it.
- **When it is quiet: exactly when CE-36's warning would be, minus the "was this op's doing" test.** That is G-W5 off in `[guards] off`, no NOW cap, NOW at or over its cap (an over-full NOW is G-W5 red with another remedy, re-rank, and it is not this item), and nothing left open. With nothing open G-W5 is green, so there is no red line to print: the everything-is-done close is quiet as well as legal.
- **The wording is CE-36's, verbatim, through one shared helper.** `_now_left`'s output stays byte-identical, so the close and G-W5 and the ops' warnings cannot drift apart.
- **FRAMEWORK.md is left alone.** §5.2 already states the rule (an op that leaves G-W5 red succeeds and says so); the close's steps live in the runbooks, which change (manual-mode § context-engine session close, procedures § Clean close step 8).
