---
type: Decision
id: DEC-247
title: "CE-190 grant shape: --grant on `ask answer` and `ask new --answered`; the words verbatim in the question's `## Grant` section, hashed into `answered: {on, session, grant}` with no `decision` key; G-W4 checks the hash, `task section` refuses Grant (refs DEC-162)"
actor: claude-code/claude-opus-5-5
refs: [DEC-162]
tasks: [CE-190]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:23ac68bf05d319b8ffd33e889711d0e580e4dec0950db9f82b7e8ad7cd4ad8f1
---

Ruled at build time under DEC-162, which leaves the exact shape of `ask answer --grant` to the builder.

`--grant` goes on `ask answer` and on `ask new --answered`. The owner's words go verbatim into the question's own `## Grant` section, as `Owner, granting ASK-n: *"<words>"*`, above `## Log`. The question closes as an answer does (`state: closed`, `status: deprecated`, `closed`, `last_asked`), and its `answered:` mapping is `{on, session, grant}`, where `grant` is `okf.body_sha` of that section's text; it has no `decision` key, and no decision record is written. Lint G-W4 checks at rest that a question whose `answered:` has `grant` holds a `## Grant` section with that hash, so the words cannot drift on a board item that is otherwise edited in place; `task section <ASK-n> Grant` is refused, since only `ask answer --grant` writes owner words there.

Rejected: a decision of any shape (tagged, or a kind of its own), since DEC-162 says none is minted; a new `ask grant` operation, since DEC-162 names `ask answer --grant` and it adds surface; the words only in a `## Log` line, which is free-form, appended by `task comment` and carries no hash.
