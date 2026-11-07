---
type: Decision
id: DEC-224
title: 'Pointer reds are a multiset: doc archive matches G-D3 failures before and after by doc and message with the leading `line N:` blanked, counting the doc and its archived copy as one doc (CE-154)'
tasks: [CE-154]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:5c6c83f50dc0d21c88b88a2b83101cc80d97457e9d12278f59b07a61b3dca84a
---

For CE-154 (CE-96's verifier finding 2): working.py::Engine.doc_archive names in its reply each G-D3 failure the archive made. It took the failures before and after the write as a Counter of (doc, message) and subtracted. But every G-D3 message opens with `line N: ` (guards.py::links, guards.py::path_pointers), so a pointer that was already red below a pruned passage changed its N and read as new, with wrong advice. A whole move shifts every line of the archived copy by two (the ARCHIVED line and its blank), so a pointer already red in it was reported as one "whose own pointers the move broke".

The call: the failures before and after are matched as a multiset (working.py::_new_reds). Each one is keyed by its doc, with the doc and its archived copy (`{rel, name}`) counted as one doc, since the write moved lines between them, and by its message with only the leading `line N: ` blanked (working.py::LINE_AT_RE). A failure after the write is new only when no failure before it has the same key left to match.

Options:
(a) multiset match on (doc, message without `line N:`), the doc and its archived copy counted as one: chosen;
(b) remap each line number through the cut and the ARCHIVED line exactly: rejected. It needs the prune's offsets, the ARCHIVED line's and CE-154's inserted `liveness:` key, and still misfires when a moved relative link changes its message;
(c) blank every digit in the message, as working.py::Engine._refuse_prose does: rejected. Messages hold ids and paths with digits, so distinct messages would merge.

Residual: when an already-red failure and a newly red one have the same message in one doc, which of the two lines is named new is arbitrary (same text, same advice).

Cost to undo: cheap (one function and its tests).
