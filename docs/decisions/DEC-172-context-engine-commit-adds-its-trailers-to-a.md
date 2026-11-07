---
type: Decision
id: DEC-172
title: context-engine commit adds its trailers to a last paragraph only when it holds a closing trailer; Sabotage lines stay body
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-11-07
session: 2026-11-07a
body_sha: sha256:33da73a481673d058fedf75222df91ed020db81a89f3261d6f269cfa254cedc1
---

`context-engine commit` (commit.py::session_message) adds `Session:` and `Co-Authored-By:` to a
message's last paragraph only when that paragraph is a closing trailer paragraph
(commit.py::_closing): trailer-shaped, with a `Session:`, `Closes:` or `<who>-by:` key
(`Co-Authored-By:`, `Signed-off-by:`, any case). Any other trailer-shaped last paragraph, the
template's `Sabotage:` lines above all, stays body, and the engine's lines open a paragraph of
their own after it.

This replaces CE-55's rule, pinned since c3c949c by
tests/test_commit.py::test_the_session_commit_carries_its_paths_with_the_op_log_and_the_records_it_names,
that any trailer-shaped last paragraph takes the trailer. Why: a work commit has no `Closes:`
(FRAMEWORK §6.10 item 1), so the CE-64 template minus the lines the engine adds ends in its
`Sabotage:` paragraph, which the template calls a body paragraph; under the old rule git read
every `Sabotage:` line as a trailer (live in 3219e82). Before CE-197 sessions wrote their own
`Co-Authored-By:` paragraph last, which hid this; now the engine writes that line, the bad
shape became the default path. Cheap to undo: one predicate in commit.py.

Not done: 3219e82 keeps its three Sabotage trailers (no history rewrite unasked). A message
that ends in a `Refs:`-only paragraph now gets a separate trailer paragraph too, so git no
longer reads `Refs:` there as a trailer; write `Refs:` beside `Session:` if it must be one.
