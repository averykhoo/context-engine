---
name: intake
description: Use the moment the owner gives intent in a repo run by context-engine (context.toml at its root) - a wish, a requirement, a choice between options, an answer to an open question, a correction of something built - before acting on it. Records the owner's words verbatim first (story, decision or ask answer), then links, criteria and questions (FRAMEWORK §6.2).
---

# Intake

Runbook: `docs/runbooks/procedures.md` § Intake

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- Record the words **verbatim, now** ... Write the words to a file with an editor, not a shell
  heredoc.
- Never `actor: owner` on the agent's own call.

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.2.
