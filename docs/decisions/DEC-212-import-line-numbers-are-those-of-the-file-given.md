---
type: Decision
id: DEC-212
title: 'import line numbers are those of the file given: the dry-run doc names that file, and there is no mapping to a log as it was before normalising'
actor: claude-code/claude-opus-5-5
tasks: [CE-171]
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:45a75b121d14fe5ebab3df7efd6055b8b67464df48ebf6b74db8161d971d135f
---

The line numbers `decision import` prints (in its summary, its refusals and the dry run's evidence doc) are those of the file it is given, counted after the CRLF to LF normalisation and the BOM strip, neither of which changes the line count. The dry-run doc says so by name: "Line numbers are those of <source>, the file this import read." There is no mapping back to a log as it was before someone normalised a copy of it: the engine never sees that original, and whoever made the copy holds the mapping.

Why: CE-171 part 3 read the CE-11 output's numbers as wrong; they were the normalised copy's, which was the file imported. Splitting on a lone `\r` (old Mac endings) as well was rejected: it changes body bytes, and no log seen uses it.
