---
type: Decision
id: DEC-99
title: ask new --answered takes the owner's words as its value, the decision title in --decision-title
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:0dc6da8c970113edfe35b5f97e30fbcc2ebdfe6e3b3c1ec4f33945f074ecaf97
---

The agent's call on CE-111, made while building it in session 2026-10-30a: how `ask new --answered` takes the owner's words and the decision title.

Options:
(a) the owner's words as the value of `--answered` / `--answered-file` (MCP `answered`), with the decision's title in a separate `--decision-title` (MCP `decision_title`);
(b) an `--answered` flag plus `--file` and `--title`, which clashes with the positional `title` (the question) as an argparse destination.

Chose (a): it matches AAR entry 14's `ask new --answered "<owner words>"`, and the positional title stays the question.

Built in lane commit 530bc18, on main as 3247ca7; pinned by AC-120. Cheap to undo: a CLI and MCP rename.
