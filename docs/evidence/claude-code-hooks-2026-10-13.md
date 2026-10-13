# Claude Code behaviours the bootloader (CE-38) and roster (CE-39) rest on

Checked 2026-10-13 (session 2026-10-13a) against the official docs at https://code.claude.com/docs/,
by five doc-reading agents, one per question; each finding below carries its page and a short
verbatim quote. READ means stated in the docs; NOT FOUND means the docs are silent and a probe is owed.

## `@`-imports in CLAUDE.md (memory)

- READ: imports load at launch with the file that names them: "Imported files are expanded and
  loaded into context at launch alongside the CLAUDE.md that references them."
- READ: "Relative paths resolve relative to the file containing the import, not the working directory."
- READ: the approval dialog is for external imports only: "An import in a project-level memory
  file is external when its path resolves outside your working directory ... The first time Claude
  Code encounters external imports in a project, it shows an approval dialog". An in-repo import
  loads with no prompt. Declining disables the imports and the dialog does not come back.
- READ: "Imported files can recursively import other files, with a maximum depth of four hops."
- NOT FOUND: what happens when the import target is missing. CE-38 probes it.

## SessionStart hooks (hooks, settings, permissions)

- READ: "Claude Code adds a SessionStart hook's plain-text stdout to Claude's context."
- READ: matchers `startup`, `resume`, `clear`, `compact`, and `fork`.
- READ: `.claude/settings.json` is the committed project file for "Team permissions, hooks, plugins".
- READ: hooks in settings files are not gated by workspace trust (permissions page, "What runs
  before you trust a folder": hooks in settings files are "Used" before trust).
- READ: a SessionStart hook cannot block: exit code 2 "Shows stderr to user only", and the session
  goes on. So a failing `orient` hook is quiet; the contract still needs its "run orient" fallback.

## MCP server instructions and tool results (mcp, security, glossary)

- READ: "Server instructions load at startup", alongside tool names and descriptions.
- NOT FOUND: any ranking of MCP server instructions against CLAUDE.md or user instructions.
- READ: tool results are named as a prompt-injection vector: "Hostile instructions embedded in a
  file, web page, or tool result that attempt to redirect Claude toward actions you never asked for".
- So "grants never arrive through MCP or `orient` output" is a design rule (REASONED), not a
  documented one: an agent that discounts authority claims in tool output is doing what the
  injection guidance asks.

## Subagents (sub-agents)

- READ: `.claude/agents/*.md` frontmatter: `name` and `description` required; optional `tools`,
  `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`,
  `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`. An unknown field is
  silently ignored.
- READ: `model` takes `sonnet`, `opus`, `haiku`, `fable`, a full model id, or `inherit`.
- READ: project agents (`.claude/agents/`) win over user agents (`~/.claude/agents/`) on a name clash.
- READ: the main thread can run as a named agent: "Pass `--agent <name>` to start a session where
  the main thread itself takes on that subagent's tool restrictions and model", or `"agent": "<name>"`
  in `.claude/settings.json`. Its system prompt replaces Claude Code's default one (unless empty);
  CLAUDE.md still loads.

## Permissions and workflow settings (permissions, settings, settings-reference, workflows)

- READ: rules are evaluated deny, then ask, then allow; MCP rules are `mcp__<server>`,
  `mcp__<server>__*` or `mcp__<server>__<tool>`; an unanchored allow glob such as `mcp__*` approves nothing.
- READ: precedence, highest first: managed, command line, `.claude/settings.local.json`,
  `.claude/settings.json`, `~/.claude/settings.json`.
- READ: a project's `permissions.allow` rules apply only after the workspace-trust dialog is
  accepted; in `claude -p` or an SDK session with an untrusted folder they are not used. Deny and ask
  rules apply at once.
- READ: `"ultracode": true` is a real setting, any scope: "Have Claude plan a workflow for each
  substantive task without being asked". `/effort ultracode` is the per-session form.
- READ: `workflowSizeGuideline` (`unrestricted`, `small`, `medium`, `large`) is a setting; it is
  advice, not a cap.
- READ: the inline keyword "is an opt-in only in a prompt you type yourself"; it does not start a
  workflow from a `-p` prompt, a scheduled task, or a relayed webhook or PR comment. A message sent in
  by another session over MCP is in the same position.
