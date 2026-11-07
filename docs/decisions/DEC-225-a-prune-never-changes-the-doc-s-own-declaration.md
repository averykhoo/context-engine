---
type: Decision
id: DEC-225
title: "A prune never changes the doc's own declaration: `doc archive --lines` refuses a cut after which G-D4 reads a different declaration in the doc itself, a word where there was none included, whatever `[guards] liveness_given` gives it"
tasks: [CE-154]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:c77c7ce8a95ede765c185549ded8c435854ed03bca3791696e4d1d610c51b072
---

For CE-154: working.py::Engine._prune refused a cut that changed the liveness G-D4 reads only when the doc declared liveness itself (`if own.word and after.word != own.word`). With the doc's liveness given only by `[guards] liveness_given`, a cut could turn a word in passing into a declaration (a wrapped line whose line above was cut now opens a block), and G-D4 then failed it ("declares X, but liveness_given gives it Y").

The call: a prune never changes the doc's own declaration. `doc archive --lines` refuses a cut after which G-D4 reads a different declaration in the doc itself, a word where the doc declared none included, whatever `[guards] liveness_given` gives it. When the doc declared a word, the refusal is today's; when it declared none, the refusal says which line would become a declaration, and names the liveness_given entry when there is one.

Options:
(a) refuse any change in what the doc itself declares: chosen. One rule, "a cut never changes what the doc declares", which _prune's docstring already stated;
(b) allow the cut when the new word equals the word liveness_given gives (G-D4 stays green): rejected, a second rule for no real gain;
(c) also check that an ACTIVE-PLAN doc's named board item stays in G-D4's window: out of scope, logged as a residual on CE-154.

Cost to undo: cheap (one condition, one message and their tests).
