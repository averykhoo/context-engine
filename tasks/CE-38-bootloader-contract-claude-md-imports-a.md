---
type: Task
id: CE-38
title: 'Bootloader contract: CLAUDE.md imports a framework-owned contract; SessionStart hook runs orient'
brief: CLAUDE.md keeps a short pointer; the framework owns its rules; grants stay in owner-loaded files, never MCP output
pri: NEXT
state: open
deps: []
source: session 2026-10-13a
created: 2026-10-13
moved: 2026-10-13a
updated: 2026-10-13a
---

Owner, 2026-10-13a (words: the story filed this session on the bootloader): an adopted framework must not depend on the owner leaving `CLAUDE.md` alone; `CLAUDE.md` gets a short pointer, like a bootloader, and the framework runs from files it owns.

Today `init` appends the whole kit contract (`kit/contract.md`, 79 lines) into `CLAUDE.md` between version markers (`bootstrap.py::BEGIN`), and G-D0 checks that block. Proposed shape, to settle in this item's design review:
- `CLAUDE.md` holds about three lines: the framework version and an `@`-import of a framework-owned contract file (e.g. `docs/framework/contract.md`), replaced wholesale on upgrade.
- A `SessionStart` hook in the repo's `.claude/settings.json` runs `context-engine orient`, so the session-start ritual does not rest on the agent obeying a rule.
- The MCP server's instructions keep saying "session_start first".
- **Standing permissions stay in owner-loaded instructions** (`CLAUDE.md` and what it `@`-imports; harness permissions in `.claude/settings.json`), never in MCP instructions or `orient` output: an agent rightly discounts a grant that arrives as tool output. Procedure may come from any of the three hooks; a grant (ultracode, `fable` cases, push rules) may not.
- G-D0 re-targeted at the pointer and the contract file's version; an upgrade path for a repo that already has the inline block.

Probe before relying on it (sabotage-style): does Claude Code load an in-repo `@`-import without an approval prompt; what happens when the import target is missing or the hook fails; does hook output reach the context on resume and after `/clear`.

Before CE-7, so adhoc adopts this shape and does not migrate twice.

## Log

- 2026-10-13a (claude-code/claude-opus-5-5): docs checked: docs/evidence/claude-code-hooks-2026-10-13.md. In-repo @-imports load at launch with no prompt (4 hops max; missing target not documented: probe it). SessionStart stdout reaches context on startup/resume/clear/compact/fork, is not trust-gated, and cannot block (a failing hook is quiet, so keep the orient fallback). Project allow rules need workspace trust. ultracode and workflowSizeGuideline are real settings; the inline keyword works only in prompts the owner types.
