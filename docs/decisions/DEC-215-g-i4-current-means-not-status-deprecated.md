---
type: Decision
id: DEC-215
title: 'G-I4 current means not `status: deprecated` (REJECTED and DEFERRED count, as G-I3 reads current); titles compare case-folded with runs of whitespace collapsed, nothing else normalised (DEC-162: mechanical only)'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-189]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:dfe1bed409ce04fdf4e2a143fa488cc272b05defe50cd806f80c923c70a26196
---

G-I4 reads a decision as current unless it is `status: deprecated` (SUPERSEDED), the same rule G-I3 uses: REJECTED, DEFERRED, BUILT, ACCEPTED and PROVISIONAL decisions all count. Two titles are the same when they are equal after case-folding and collapsing runs of whitespace; nothing else is normalised.

Options: (a) case and whitespace only; (b) also strip punctuation; (c) a fuzzy match (edit distance, word sets).

Chose (a). DEC-162 asks for mechanical checks only, with no semantic conflict detection. Stripping punctuation or fuzzy matching would fail pairs whose titles were chosen to differ, and would still miss a paraphrase. Titles that differ in a word or in punctuation are named in the guard's "Not checked" list.

Cost to undo: cheap; change the key function.
