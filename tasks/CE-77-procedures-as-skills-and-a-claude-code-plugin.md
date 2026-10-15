---
type: Task
id: CE-77
title: Procedures as skills, and a Claude Code plugin bundling the skills, the SessionStart hook and the MCP server
brief: Contract stays always-on (CLAUDE.md import + hook), not a skill; every skill keeps its runbook as by-hand fallback
pri: NEXT
state: closed
deps: []
source: session 2026-10-14c
created: 2026-10-14
moved: 2026-10-15a
updated: 2026-10-15a
status: deprecated
closed: 2026-10-15a
---

Package the on-demand parts of the framework as Claude Code skills, and ship them with the
SessionStart hook and the MCP server as one Claude Code plugin, so a repo adopts the framework
with one install instead of `claude mcp add` per machine and project plus init writing
`.claude/settings.local.json`.

## Scope

- **Skills for the procedures** in `docs/runbooks/procedures.md`: intake, clean close, pause,
  resume, push and CI, bootstrap, reconciling foreign commits, housekeeping. Each skill triggers
  when the procedure starts and gives its steps; the runbook stays the source and the by-hand
  fallback (DEC-20). Decide one skill per procedure vs one umbrella skill from what the adhoc trial
  (CE-7) shows sessions forgetting to read.
- **An adoption skill** ("bring this repo under the framework", CE-15, CE-43): init, gate, import,
  board rows, HANDOFF trim. CE-7's trap list is its first draft.
- **A plugin** bundling those skills, the SessionStart hook (orient) and the MCP server
  registration.

## Out of scope

- The contract (`docs/framework/contract.md`) is not a skill. Its rules must hold every session
  whether or not a description matched; a skill that never triggered fails silently (P7). It stays
  in the CLAUDE.md import plus the hook.
- The engine stays a CLI and package runnable without Claude Code (actor is `<harness>/<model>`;
  DEC-1, DEC-20).

## Traps

- Engine pinning (CE-7 trap F18): one plugin-installed engine shared across repos turns a repo's
  lint (G-D0) red on any kit change made elsewhere. The plugin's hook and MCP entry must run each
  repo's pinned engine env, not one shared one.
- Kit byte-equality (CE-26): if skills copy runbook text, the gate must keep them in step, or the
  skills only point at the runbook.
- DEC-32 (settings merge) and init's hook writing change if the plugin carries the hook: decide
  whether init still writes it, and avoid running orient twice.
- FRAMEWORK.md says the kit ships no skills (§ layout, `.claude/skills/`): update it in place
  (DEC-19), and the G-7 coverage map (CE-16).
- Sabotage rule (DEC-11) for any guard added: e.g. a test that the plugin manifest names a hook
  and MCP command that exist.

## Read first

- `docs/evidence/claude-code-hooks-2026-10-13.md` (settings, plugins, hooks as read 2026-10-13)
- `src/context_engine/kit/README.md` (init, § Hook), DEC-32, DEC-1
- `docs/runbooks/procedures.md`, CE-15, CE-16

## Log

- 2026-10-14c (claude-code/claude-opus-5-5): Owner, 2026-10-14c, verbatim: "okay yes file a task to make skills and bundle the plugin" (answering the session's proposal: procedures and adoption as skills, a plugin for the hook and MCP setup, after the adhoc trial).
- 2026-10-14g (claude-code/claude-opus-5-5): DEC-43 (owner, 2026-10-14g): start now; the CE-7 dep and the 2026-10-14c freeze are lifted for this task. adhoc keeps its pinned kit (DEC-41).
- 2026-10-15a (claude-code/claude-opus-5-5): closed: done in 2b32f4c (merge), 93f1939 (tests meet CE-78's scope guard), 6f00cb2 (README § 1 reconciliation)
