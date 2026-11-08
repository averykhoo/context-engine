---
type: Decision
id: DEC-249
title: 'CE-190 grant refusals, before any write: a decision title, a ruling or ruled_by, empty words, a `## ` heading line in the words, an unset [working] ledger, a session with no open stub'
actor: claude-code/claude-opus-5-5
refs: [DEC-162]
tasks: [CE-190]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:37940f1c03756ebcf7045515fc8b263ae587ef54552f137b9b8697bf4660e061
---

Ruled at build time under DEC-162.

`ask answer --grant` and `ask new --answered --grant` refuse, before anything is written: a decision title (a grant mints no decision); a ruling or `ruled_by` (a ruling on the owner's delegation is a call, recorded as a decision: drop `--grant`); empty or whitespace-only words; words holding a line that starts `## ` (it would end the `## Grant` section, so the hash would cover only part of the words); an unset `[working] ledger`, and a session with no open `kind: open` stub (the `granted:` bullet has nowhere to go, and the close could not ask for the quote). The existing refusals still apply: not a question, already closed, open but carrying `answered:`, and a frozen plan naming the question.
