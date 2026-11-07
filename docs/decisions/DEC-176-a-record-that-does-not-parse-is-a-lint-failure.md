---
type: Decision
id: DEC-176
title: A record that does not parse is a lint failure naming it, never a crash (CE-161)
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-07
session: 2026-11-07d
body_sha: sha256:2f3e7672b546a027af6111b250f91477584c916622124b7d0561abfe66c87355
---

CE-161: a record that does not parse (not UTF-8, not valid YAML, no closing `---`) is a lint failure naming the file, never a crash, and stops only a commit that carries it.

How:
- `store.py::Store.lint` reports it as a `schema` failure, `does not parse: <why>`, at the record's path; `lint --working` runs that check too (`Store.lint(unreadable_only=True)`), since it would otherwise pass over the record in silence.
- `working.py::Engine.lint` runs every guard inside `store.py::Store.skipping_unreadable`, where `Store.heads` and `Store.records` pass over a record that does not parse instead of refusing. The schema failure is the one report of it.
- Outside lint, `Store.heads`, `Store.records` and `Store.get` refuse naming the file (`<path> does not parse: <why>`), so `task list`, `task show` and every other reader say which file to fix. They do not pass over it: a list that silently drops a record would mislead more than a refusal that names it.
- `Store.read` and `okf.read_head` turn bytes that are not UTF-8 into a Refusal (they let `UnicodeDecodeError` out before, which crashed lint), and `okf.read_head` no longer puts the absolute path in its message: the caller names the file.

So `working.py::Engine._lint_carried` sees the failure at the record's path and refuses a commit only when it carries that path, naming it; a commit of other paths goes in.

Alternatives not taken: making `Store.heads` always skip a broken record (silent everywhere outside lint); catching the exception around each guard in lint (a guard that raised would lose every other failure it would have found).
