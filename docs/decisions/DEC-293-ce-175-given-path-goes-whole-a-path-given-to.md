---
type: Decision
id: DEC-293
title: 'CE-175 given path goes whole: a path given to `context-engine commit` is always committed as the whole working file'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:7ead965e2b177726f77fe07cef28fd5ce3e7d8fdd607ff2669d6ac2e3c3bb33c
---

A path given to `context-engine commit` explicitly is always committed as the whole working file,
the orientation note included, even when the only op lines naming it are `banner.set`: an explicit
path is its author's own commit, whatever it holds. This is how the hand edits a banner-only commit
left behind get committed (CE-175).
