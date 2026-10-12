<!-- context-engine kit 0.5 begin -->
## Framework

framework: 0.5

This repo runs the context-engineering framework (FRAMEWORK.md, in the engine repo at the
pinned ref) through the record engine, `context-engine`. `§` references below are FRAMEWORK
sections. What is true now and what is next live in `HANDOFF.md` and on the board
(`context-engine task list`); this block holds only what is durable. Where each component lives
is `[[routes]]` in `context.toml` (`context-engine routes`); the record kinds and their schemas
are `[kinds.*]` there too.

### Environment

- **The engine runs from its own environment and is never installed into this repo's.**
  `<engine-python>` below is that environment's interpreter. `context-engine` means
  `<engine-python> -m context_engine`, run from this repo's root, with `CE_ACTOR=<harness>/<model>`
  and `CE_SESSION=<key>` set in every command (shell state does not persist between tool calls).
- **The MCP server** carries the same operations as `mcp__context-engine__<group>_<verb>` tools.
  Claude Code starts it per session over stdio; nothing is run by hand. Call
  `session_start(actor=...)` first: the server remembers the key and actor.
- **Set-up, once per machine:** `claude mcp add --scope local context-engine -- <engine-python> -m
  context_engine.mcp` (stored in `~/.claude.json` for this project, never committed: the path is
  machine-specific). `claude mcp get context-engine` prints the interpreter it was given.
- **If the MCP tools are missing at session start,** register the server as above, run every
  operation through the CLI for the rest of the session (same functions, nothing lost), and ask
  the owner to restart Claude Code.

### Gate

`<this repo's own test command> && context-engine lint`, from the repo root. Run it before every
commit that touches code, tests or any record, and before every push. Lint covers the record
schemas, append-only bodies, bundles, the working state and the routes; it fails on a hand edit
to a stamped record, a broken record or a dead route.

### Rituals

Session start, intake, clean close and pause are FRAMEWORK §6.1 to §6.4, each step a
`context-engine` operation. When the engine errors or refuses something it should allow, do that
step by hand from the manual-mode runbook (`docs/runbooks/manual-mode.md`, here or in the
engine repo at the pinned ref), then report the engine bug. A refusal with a sensible remedy is not an error: follow the remedy.

### Rules

**Ultracode** (the `Workflow` tool, multi-agent orchestration) needs no per-request opt-in when
it keeps the session's own context and tokens down: bulky reading, auditing or verification
pushed into agents, only verdicts kept.
- The test is shape, not permission: a real fan-out with a reconcile step;
- not a cheap lookup, and not coupled work split up to go "faster".

**Several tasks in one session:** when one request asks for more than one task,
- each task goes to its own subagent, which owns it end to end and can persist (not `Explore`);
- that task agent pushes the work down again, to its own subagents or a workflow;
- the top-level conversation stays clear: progress, blockers and delays, then the digest;
- judgement and owner words stay at the top: the session records owner words verbatim (§6.2)
  and verifies first-hand before a commit, a push or a record write;
- tasks that touch the same files go to one agent or run in sequence (disjoint ownership,
  below).

- **Do not use `fable` subagents unless the owner asks for them or they are really necessary.**
  Never fan out with fable: it wastes tokens.
- Commit by path (`git commit -o <paths>`); never `git add -A`, never `git stash`: sessions may
  share the working tree.
- Push (§6.8): gate before every push; push only with permission; a background CI watcher for
  every push, keyed on the commit hash; the push is not done until the watcher reports; the
  watcher only watches.
- Never hand-edit what an operation owns: `body_sha`, `type`, `id`, a board item's `state`,
  `status`, `pri`, `deps`, `moved`, `updated`; a story's or decision's text above
  `## Amendments`.
- Never reuse or renumber an id.
<!-- context-engine kit 0.5 end -->
