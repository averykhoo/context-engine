---
type: Decision
id: DEC-228
title: 'Re-read before writing: doc archive re-reads the doc, the archive file and the table before its first write, and refuses, writing nothing, if any changed since it read them'
tasks: [CE-154]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:bec1664a16f545795fe3ae594e91defde063576db428f729a1ab00441647e647
---

For CE-154: working.py::Engine.doc_archive reads the doc, the archive file and the redirect table, then runs G-D3 over the repo (guards.py::links, slow) before it writes. An edit made in between, by a hand or another session, was overwritten: a `--lines` range was not re-checked against the doc as it now stood, and a line added beyond it was lost.

The call: doc archive takes the bytes of the doc, the archive file and the table (or that each is absent) before it reads them, and re-reads them after G-D3's first run, before its first write. If any of them changed, it refuses, writing nothing, and says to run it again and check the range against the doc as it is now.

Options:
(a) snapshot and re-check before the first write: chosen;
(b) no re-check: rejected, the finding;
(c) hold a file lock other tools honour: not available; an editor or another tool does not take the engine's lock.

Residual: a small window remains between the re-check and the write (TOCTOU).

Cost to undo: cheap (one check and its test).
