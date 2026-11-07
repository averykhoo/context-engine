---
type: Decision
id: DEC-171
title: "Co-Authored-By on every engine commit: from --co-author, --model, CE_CO_AUTHOR, then the actor's model; none for a person"
decision_status: PROVISIONAL
tasks: [CE-197]
actor: claude-code/claude-opus-5-5
decided: 2026-11-07
session: 2026-11-07a
body_sha: sha256:fcac1eba4e0bc895bc8aa096e2ad11bd3ab9a4c95e5caa22aa3b504b481ad252
---

An agent's call under P8 (cheap to undo), made by CE-197's builder in session 2026-11-07a, carrying out DEC-170 (the owner's words). Not owner words.

**Calls.**
1. **Where the line comes from, first hit wins:** `context-engine commit --co-author "<name> <email>"` (MCP `co_author`), or `--model <model-id>` (MCP `model`; the two exclude each other); then `CE_CO_AUTHOR` in the environment; then the actor's model, read from `<harness>/<model>`. `claude-code/claude-opus-5-5` gives `Claude Opus 5.5 <noreply@anthropic.com>` (`commit.py::model_name`: numeric parts joined by dots, words capitalised, a date, a `[1m]` suffix, a `@<date>` or `-v1:0` version and a provider prefix dropped, an alias such as `opus` read as `Claude Opus`). A `claude...` harness whose model it cannot read gives plain `Claude <noreply@anthropic.com>`, as DEC-170 allows.
2. **Who gets none:** an actor with no `/` (`human:<id>`, `process:<id>`), so a person's commit never says an agent co-wrote it; and a non-Claude harness whose model is not Claude's (`codex/gpt-5`), since the engine knows no address for it: `CE_CO_AUTHOR` or `--co-author` names one. The opt-out for an agent is the value `none` (`--co-author none`, `CE_CO_AUTHOR=none`), not a separate `--no-co-author` flag: one option fewer on the CLI and the MCP tool.
3. **Every engine commit, not only `commit`:** the milestone commits (task close, owner words, batons, pauses, session close) name the actor of the batch's last write. A malformed `CE_CO_AUTHOR` cannot refuse a milestone commit, which follows a write already made, so there it is ignored and the actor's model is used; the session's own `commit`, which writes nothing first, refuses it.
4. **One trailer paragraph, no duplicate:** the line goes into the message's last paragraph after `Session:` (after `Closes:` and `Session:` on a close). A `Co-Authored-By:` line already in that paragraph for the same address (in any case, under any name) stands and ours is not added; one for another address is kept and ours is added beside it (two co-authors). Only the last paragraph is read, as git reads it, so a trailer-shaped prose paragraph earlier in the message is never merged into the trailers.

**Why.** DEC-170 asks for the line always, with the right model where the engine can tell, and a flag otherwise. The actor already carries the model id (CLAUDE.md sets `CE_ACTOR=claude-code/<model-id>` in every command), so reading it there needs nothing new from the session; the flag and the env var cover a harness the engine cannot read, and `none` covers the rare agent commit that must not carry it.

Task: CE-197.
