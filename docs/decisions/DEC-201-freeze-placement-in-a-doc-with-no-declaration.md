---
type: Decision
id: DEC-201
title: 'Freeze placement in a doc with no declaration: after its H1 (past the blank line that follows it), else first after its frontmatter, else line 1; never a new frontmatter key'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:27259ff85dcd5caec147172d1e90bbfb2a5f639e4fc8e0e228bce736c95da3f0
---

In a doc that declares no liveness, `doc freeze` puts the FROZEN line (and a blank line below it) where archive.py::opening says. If the first non-blank line after any frontmatter is an ATX H1, the line goes after the title, past the blank line that follows the title when one does. Otherwise, in a doc with frontmatter, it goes first after the frontmatter. Otherwise it is the doc's first line. Rejected: always line 1, which would move the title off the first line, while every doc here puts the H1 first and the declaration after it (ARCHIVED goes first only because FRAMEWORK §7.3 says so). Also rejected: adding a `liveness: FROZEN` key to a frontmatter that has none, which edits YAML, the reason the keyed case is already refused; archive.py::archived already puts its line first after the frontmatter. CE-172.
