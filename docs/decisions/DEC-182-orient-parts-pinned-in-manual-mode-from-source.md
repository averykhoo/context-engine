---
type: Decision
id: DEC-182
title: Orient parts pinned in manual-mode from source
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:b6154e86bfaf8a8340a297dbb41b08f8d2b9e68d585e2a970fa9d53926d3de6d
---

manual-mode § context-engine orient names every part heading `working.py::Engine.orient` emits, each in backticks at its first mention, in the order orient shows them. Two tests in `tests/test_runbook.py` pin it by reading `Engine.orient`'s source (each `Part("<title>"` literal, f-string placeholders read as `<...>`), with a floor on the count so a regex that stops matching goes red.

Rejected: a hand list of titles in the test (it drifts exactly as the runbook did: CE-121, CE-136 and CE-185 each added a part); running orient on a fixture that triggers all 22 parts (costly and slow for a docs pin); an AST walk (sturdier against formatting, but more than this needs while every call is `Part(` plus a literal, and the count floor catches a regex that stops matching). Residual: a title built in a variable would be missed unless the count drops below the floor.

Made for CE-200.
