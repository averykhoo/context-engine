---
type: Decision
id: DEC-229
title: 'Kit task prefix: the template holds the placeholder TASK; init on a repo with no context.toml refuses without --prefix task=, and its dry run warns instead'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:99654bda8c4aa95acf6c88dd27345c523ed31895b1a3e41778aaeba6dbd48554
---

For CE-56 (DEC-38's kit-defaults half): the kit's template gave tasks the prefix T, so every repo that ran a bare `init` got a one-letter task series that collides with ordinary labels, and nobody chose it.

The call: the kit template's `[kinds.task]` holds the placeholder prefix TASK. `init` on a repo with no `context.toml` refuses without `--prefix task=<PREFIX>`, writing nothing, and its remedy says to ask the owner for 2 to 5 capitals naming the board; `init --dry-run` warns instead of refusing, so the owner sees the whole plan first. A re-run on a repo whose `context.toml` exists needs no prefix.

Options:
(a) refuse without a task prefix, warn on a dry run: chosen;
(b) an interactive prompt: rejected, agents and the MCP server have no TTY;
(c) guess the prefix from the folder name: rejected, a guess the owner did not make, and it can collide;
(d) keep T as the default: rejected, DEC-38 gives tasks a per-repo prefix.

Cost to undo: cheap (one refusal, one warning and their tests).
