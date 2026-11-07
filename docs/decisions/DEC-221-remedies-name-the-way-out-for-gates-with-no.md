---
type: Decision
id: DEC-221
title: "Remedies name the way out for gates with no pass count: the session close refusal and the lint G-W6 remedies say to fit [working] gate_receipt to the gate's result line or set it to ''"
tasks: [CE-192]
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:5189abb739024748d06863435202a3b91f534cf9bede8b384336626ff37d65ef
---

The agent's call on CE-192: what a refused close and a failing lint G-W6 tell a repo whose gate prints no pass count.

Now that the check is on where nobody opted in, a repo whose gate prints e.g. `ok <pkg> 0.1s` (go test) has no `N passed` to quote. The remedies of working.py::Engine.session_close's gate_receipt refusal and of lint G-W6 (working.py::Engine._gate_receipt_problem) therefore also say: for a gate that prints no pass count, fit `[working] gate_receipt` to its result line, and `''` turns the check off. They keep the words "pass count" and "gate_receipt", which a test asserts.

Cost to undo: cheap.
