---
type: Decision
id: DEC-250
title: "CE-190: `ask answer` without --grant has its empty title refused by the engine; the CLI drops required=True on --title and the op's title defaults to \"\""
actor: claude-code/claude-opus-5-5
refs: [DEC-162]
tasks: [CE-190]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:65eb3e90b6a7d5bd7732ed43d10c0c0dc7483ea9994e6e98f5fe45c0d8723371
---

Ruled at build time under DEC-162.

With `--grant` taking no title, `ask answer --title` is no longer required by argparse: the CLI drops `required=True`, the operation's `title` defaults to `""`, and the engine refuses a plain `ask answer` (no `--grant`) with an empty or whitespace-only title, naming `--title` and `--grant`. The MCP tool, built from the operation's signature, gets the same default, so both front ends meet the one refusal.
