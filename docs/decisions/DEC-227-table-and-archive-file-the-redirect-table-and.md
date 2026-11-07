---
type: Decision
id: DEC-227
title: "Table and archive file: the redirect table and `<stem>-pruned.md` may carry uncommitted changes only where an uncommitted op line (any session's) names them; the doc being archived must be clean"
tasks: [CE-154]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:2819ef59d5795b99856dd4f200152d23c53acc57c0c5b07fbae3026739401fa2
---

For CE-154: working.py::Engine.doc_archive refused a doc with uncommitted changes, but appended its row to the redirect table (`<dir>/README.md`) and a pruned passage to `<dir>/<stem>-pruned.md` with no check on those files. A hand edit to either rode into the archive's commit unseen.

The call: the redirect table and, for a prune, the archive file may carry uncommitted changes only where an uncommitted op line, any session's (commit.py::pending with no session, as working.py::Engine.pause_open reads it), names them; otherwise `doc archive` refuses, writing nothing. The doc being archived stays strict: it must be clean in git, op line or not, since the lines named are the lines in git.

Options:
(a) the table and the archive file may be dirty only where an op line names them: chosen;
(b) refuse any dirty table or archive file: rejected. Two archives in a row before a commit, which DEC-36 allows (an archive is not a milestone), would be refused;
(c) no check: rejected, the finding.

Residual: a hand edit on top of an engine-written, still uncommitted table passes, since op lines carry no content hash.

Cost to undo: cheap (one check and its tests).
