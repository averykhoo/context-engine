---
type: Decision
id: DEC-89
title: New criterion AC-101 for CE-138's refusals, not a rewrite of AC-98, AC-99 or AC-100
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:a5c075908f8bfbcfb4e032852e610d869ce981bfea30295d5e56461104eb4dd8
---

CE-138's refusals get a new criterion, AC-101, rather than a rewrite of AC-98, AC-99 or AC-100.
This keeps the text of criteria that are already tested stable (P14).

AC-101: `record new` of a decision and `ask answer` refuse a `ruled_by` or a lone `actor` naming
the owner in any case, and a decision text holding `## Amendments` (the remedy names `record
amend`); G-I3 fails a hand-edited `ruled_by: Owner` or `actor: Owner`. From US-7, state tested,
sabotaged as the CE-138 commit lists.

Options weighed:
- A new criterion: chosen.
- Rewrite AC-98, AC-99 or AC-100 to cover the new cases: rejected, it changes the text of tested
  criteria under their existing claims.

Landed in the CE-138 commit (lane commit de6d55e, integrated on main as 9700437).
