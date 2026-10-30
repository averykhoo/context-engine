---
type: Decision
id: DEC-123
title: A partial prune is doc archive --lines A-B, into one <stem>-pruned.md per source with one redirect row per prune
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
tasks: [CE-96]
code: [src/context_engine/working.py::Engine._prune, src/context_engine/working.py::_line_span, src/context_engine/archive.py::cut, src/context_engine/archive.py::pruned]
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:987798fe9bb0c0b7e8fe48587f13177c092dca01a53a85c1802f3d5b66ad1f14
---

A partial prune is `doc archive --lines A-B` (CE-96).

Shape: an explicit line range (the session judges what goes, the engine makes the cut); one archive file per source stem, `<dir>/<stem>-pruned.md`, each prune under `## Pruned from <doc> on <date>`; one redirect row per prune, its first cell `<doc> lines A-B`; refused on a doc with uncommitted changes, so the lines named are the lines in git.

Options considered: a separate `doc prune` op (more surface: a new op, MCP tool and op-log name); selecting a section by heading (cannot cut part of a section); one redirect row per archive file (loses which lines went where). Chose `--lines` on `doc archive`.

Why: it reuses the `doc.archive` op, and every guard (frontmatter, FROZEN, a change to the liveness G-D4 reads, a blank passage, past the end, the whole doc) is checked before any write.

Known gap (CE-96 verifier): the liveness-change refusal runs only when the doc declares liveness itself; a doc whose liveness comes only from `[guards] liveness_given` can have a cut turn a word in passing into a declaration.

Code: working.py::Engine._prune, working.py::_line_span, archive.py::cut, archive.py::pruned, archive.py::pruned_heading.
