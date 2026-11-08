---
type: Decision
id: DEC-254
title: "CE-196: register retire's why is one line without brackets (the heading marker is parsed by brackets); empty only with --into"
actor: claude-code/claude-opus-5-5
tasks: [CE-196]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:e5f9f1aeaa5052f0c428115e62d1977b098d3930f1de445f91b146c41558ad2e
---

A build-time call for CE-196, the agent's own, PROVISIONAL until the owner reviews it.

`register retire`'s `--why` is one line with no round brackets, because the heading's `(retired <session>: <why>)` marker is found by its brackets. A `:` is allowed. An empty why is refused unless `--into` is given, since then the merge itself is the reason. There is no `--file`: the why is the agent's one-line reason, not owner words.
