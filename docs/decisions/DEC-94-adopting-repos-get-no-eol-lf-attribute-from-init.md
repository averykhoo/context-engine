---
type: Decision
id: DEC-94
title: Adopting repos get no eol=lf attribute from init
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:2acf25a40043ce0d1a8bd0a55e64916327f2873c281b6ae437823274adf3de69
---

The agent's call on CE-46, made while building it in session 2026-10-30a: whether `init` should pin line endings in an adopting repo.

Options:
(a) `init` also writes `eol=lf` lines for the kit copies into the target's `.gitattributes`;
(b) none, since every target-side check compares line endings aside.

Chose (b). The CE-46 test (tests/test_kit.py::test_line_endings_change_nothing_init_writes_or_lint_checks_in_an_adopting_repo, AC-115) shows that init from a CRLF kit writes the same bytes as from an LF one, and that a CRLF checkout of an initialised repo lints clean and init re-runs as a no-op. Forcing an `eol` attribute on an owner's files is intrusive. Only the engine repo pins `eol=lf` (20b1ad9), because its own tests compare kit bytes.

Known gap at landing: lint is exercised only against the LF kit; an engine installed from a CRLF checkout linting an LF repo is not exercised, though the normalisation is symmetric.

Built in lane commit ec4dd4d, on main as 4cc4e1a. Cheap to undo: add the attribute lines to init's plan.
