---
type: Decision
id: DEC-226
title: "Long frontmatter gets a FROZEN key: when the ARCHIVED line would fall past G-D4's window and the frontmatter has no `liveness:` key, the archived copy gets `liveness: FROZEN  # ARCHIVED <date>` as its first frontmatter key; a `liveness:` key outside the window refuses the archive"
tasks: [CE-154]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:2cbb614e2de1457c162e9eea3b688756b4bf909dd62a8988d7d5d8920379b2e6
---

For CE-154: archive.py::archived puts the ARCHIVED line first after a doc's frontmatter. When the frontmatter runs long (with the default `[guards] liveness_lines = 10`, a `---`, 8 keys and a `---`) the ARCHIVED line falls past G-D4's window, and with no `liveness:` key in the frontmatter the archived copy read as no liveness: G-D4 red.

The call: when the doc has frontmatter, no line of it is a `liveness:` key (guards.py::FM_LIVENESS_RE, FROZEN or not), and the ARCHIVED line would sit past the window (`end + 2 > window`, `end` the 0-based index of the closing `---`), the archived copy gets `liveness: FROZEN  # ARCHIVED <date>` as its first frontmatter key, in the doc's own line ending. Every other case keeps its bytes. Before any write, working.py::Engine.doc_archive reads the archived copy as G-D4 does (guards.py::declared) and refuses the archive, writing nothing, unless it reads FROZEN: that is the case of a `liveness:` key that lies outside the window.

Options:
(a) insert a FROZEN key first in the frontmatter, and refuse when a liveness key lies outside the window: chosen;
(b) put the ARCHIVED line above the frontmatter: rejected, it stops being frontmatter;
(c) a second `liveness:` key, or moving the existing key up: rejected, a duplicate YAML key, or a repair of the archived material (FRAMEWORK §7.3 moves it unrepaired);
(d) refuse every long frontmatter: rejected, the common case is fixable mechanically;
(e) a note in the reply only: rejected, lint stays red.

Cost to undo: cheap (one insertion, one refusal and their tests).
