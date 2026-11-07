---
type: Decision
id: DEC-202
title: doc freeze re-reads its result with G-D4's reading (guards.declared) and refuses, writing nothing, unless the inserted line is now the doc's FROZEN declaration inside the window
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:8fc2d5affccb3e07a98ac4975e1d15052200ce1bbe0b77b4093e0e6b26617541
---

When `doc freeze` writes a FROZEN line into a doc that declared none, it first re-reads the new text with G-D4's own reading (guards.py::declared, in `[guards] liveness_lines`). Unless that reading finds FROZEN at the inserted line, it refuses and writes nothing, and the remedy says to write the line by hand within the window or raise `liveness_lines`. A long frontmatter or a run of blank lines can put the placement outside the window, and without this check G-D4 would stay red after a reply that reported success. CE-172.
