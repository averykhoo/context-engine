---
type: Decision
id: DEC-122
title: Archiving a doc whose frontmatter declares liveness turns that key FROZEN, keeping the old value in a comment
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
tasks: [CE-96]
code: [src/context_engine/archive.py::frontmatter, src/context_engine/archive.py::thawed_keys, src/context_engine/archive.py::archived]
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:9fb0ab2cb7fa6b2c6fea1cc6d65fe59bd28dc71288ba82b0b7dc9ac9909dc7ce
---

Archiving a doc whose frontmatter declares `liveness:` turns that key FROZEN (CE-96).

Options: (a) refuse, and leave it as a by-hand step; (b) put the ARCHIVED line after the frontmatter and leave the key; (c) do (b) and also rewrite the key as `liveness: FROZEN  # ARCHIVED <date>; was <old value>`. Chose (c).

Why: G-D4 reads the frontmatter key before any line below it, so under (b) an archived doc would still claim LIVING. The old value is kept in a YAML comment. The CE-96 brief names this case as one to automate.

Code: archive.py::frontmatter, archive.py::thawed_keys, archive.py::archived.
