---
type: Decision
id: DEC-87
title: AC-53's provenance list names ruled_by
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:1057bc8749aba8851ab1633c224b73f853bf42d4e6851b16da7fe6dc0f8b9f71
---

AC-53's text in `docs/criteria.md` now lists `ruled_by` among the provenance keys. This catches the
criterion up with the `ruled_by` parametrize row its test already has (CE-113).

Options weighed:
- Amend AC-53 in place: chosen. It keeps the id its tests claim (P14).
- Retire AC-53 and re-add it under a new id: rejected, it moves a tested criterion's id for a
  wording catch-up.
- Leave the drift: rejected, the criterion would name less than its test checks.

No test was changed to make anything pass.

Landed in the CE-138 commit (lane commit de6d55e, integrated on main as 9700437).
