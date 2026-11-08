---
type: Decision
id: DEC-292
title: "CE-175 banner-only commit: a banner.set commit carries HEAD's orientation note with the working banner grafted in; hand edits outside the banner stay uncommitted for their author to commit by path"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:019ccbe0d678251de4b071679ea813003b4d11d1012cbe6edb5e9af95fdc324e
---

An engine commit (a milestone, or the session's own `context-engine commit`) that carries the
orientation note (`[working] handoff`) only because op lines name it, where every such uncommitted
line is `banner.set`, carries HEAD's note with the working note's banner grafted in
(`commit.py::banner_only`, `commit.py::_banner_grafts`), not the working file. Hand edits outside the
banner, anyone's, stay uncommitted in the tree, and the reply says so; whoever made them commits the
note by path. Why: the orientation note is the one file the engine shares with hand edits, and a
banner commit inside a milestone the session does not choose (`session close --banner`) swept another
session's half-done edit under this session's name (CE-175 repro, 2026-11-08). Rejected: refusing
`banner set` while the note has other edits (blocks a clean close on another session's work), warning
only (still publishes the half-edit, as CE-125 rejected for op lines), documenting only (the sweep
happens inside a milestone), and a hunk-level partial commit for every record (records are op-owned;
INV-42 accepts that window).
