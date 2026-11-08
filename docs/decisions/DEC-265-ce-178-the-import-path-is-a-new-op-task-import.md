---
type: Decision
id: DEC-265
title: 'CE-178: the import path is a new op, task import <file> (JSON Lines of id, fields, body), not a Store helper or a markdown directory'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-178]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:263492499998e3645b598483566edfe52bcbb81fbc0d02d7228bc00f07df63ae
---

A build-time call for CE-178, the agent's own, PROVISIONAL until the owner reviews it.

The import path is a new operation, `task import <file> [--kind <board kind>]` (MCP `task_import`), reading JSON Lines: one object per line with `id`, `fields` and an optional `body`, and no other key. Not a Store-only helper (an adopter would need Python against the engine's internals, and DEC-20 wants an operation with a runbook fallback), and not a directory of markdown files (YAML retypes values such as `moved: 2026-07-29` into dates, the files would carry `type` and `id`, and a long body is not bounded by a command line, CE-174's trap).
