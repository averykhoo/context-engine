---
type: Decision
id: DEC-104
title: A bare ask new with no body is refused; the CLI takes --body-file
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:921e50cdb7a69f65a9a6e7a0085b8769044a6292fb01d422c5b92e57666e6542
---

The agent's call on CE-44, made while building it in session 2026-10-30a: a bare `ask new "<title>"` with no body is refused.

Options:
(a) refuse it, and give the CLI `--body-file`; every runbook `ask new` command shows `--body-file <ask.md>`;
(b) keep filing the template skeleton as the default body.

Chose (a): the template only names the parts, so a default body would always fail the three-part check (and G-W4). The follow-up remedy (working.py::answered_remedy) names `--body-file` too.

Built in lane commit 143bb4b, on main as 10f8717. Cheap to undo: restore the default body and drop the refusal for it.
