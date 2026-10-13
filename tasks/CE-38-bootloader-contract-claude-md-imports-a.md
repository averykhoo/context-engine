---
type: Task
id: CE-38
title: 'Bootloader contract: CLAUDE.md imports a framework-owned contract; SessionStart hook runs orient'
brief: CLAUDE.md keeps a short pointer; the framework owns its rules; grants stay in owner-loaded files, never MCP output
pri: NOW
state: open
deps: []
source: session 2026-10-13a
created: 2026-10-13
moved: 2026-10-13b
updated: 2026-10-13b
review: [shipped, guard]
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
- 2026-10-13b (claude-code/claude-opus-5-5): Owner, 2026-10-13b: "Let's try to get it ready for first use then trial it on a repo": CE-38 then CE-7 (the trial) lead; CE-25 waits on ASK-3.

## Read first

- US-17 (the owner's words) and DEC-30 (grants stay in owner-loaded files; asking may come from MCP)
- `docs/evidence/claude-code-hooks-2026-10-13.md`: what Claude Code documents about @-imports, SessionStart hooks, MCP instructions, subagents and permissions
- `src/context_engine/bootstrap.py` (the inline contract block today) and G-D0 in `src/context_engine/working.py`

## Design review

affects: every adopting repo (CE-7's is the first) and its owner, whose CLAUDE.md init appends to and whose machine gets a local settings file; every agent session there, whose rules now load through one import and whose orient arrives by a hook; this repo's gate, through G-D0 and the kit tests
- eliminated: an upgrade overwrites the repo's own rules in CLAUDE.md: the framework owns only the region between the kit markers and the imported file, and the repo's rules (the gate command included) live outside the markers
- eliminated: init clobbers a local settings file holding the owner's permission grants: it creates `.claude/settings.local.json` only when absent (create-only, refused if it appears mid-run) and never merges into one
- eliminated: a grant reaches a session through the hook or MCP output (DEC-30): the hook prints orient, which carries procedure only; the grants stay in the imported contract, loaded from CLAUDE.md
- reduced: the import target is missing or moved, so a session runs with no framework rules | rung: reduce | control: G-D0 reds a kit block whose import target does not exist (gate and CI); orient leads with a "Contract: fix this first" section when G-D0 is red, so the hook's output says it; the bootloader text itself says to read the file and run lint
- reduced: a hand edit to the imported contract, or a stale copy after the engine moved, drifts from the engine's rules | rung: reduce | control: G-D0 reds when the imported file differs from the installed engine's kit/contract.md (line endings normalised), naming the copy as the fix
- reduced: a repo bootstrapped with the inline block keeps it, or gets a second block | rung: reduce | control: init never adds a second block and names the by-hand replacement; G-D0 reds a current-version kit block that is not the kit's bootloader, naming the upgrade steps
- residual: the SessionStart hook does not run (another clone or machine, a moved interpreter, an existing local settings file init skipped), and a failing SessionStart hook is quiet by design | rung: individual | why: Claude Code documents that a SessionStart hook cannot block, and the local settings file is machine-specific and gitignored, so lint cannot see it | control: the contract's session-start rule: if no orient output is in context, run session start and orient by hand and tell the owner the hook did not run
- residual: Claude Code's behaviour on a missing @-import target, and whether hook output reaches context on resume and after /clear, are documented only in part and not probed on a live session | rung: individual | why: a probe needs an interactive Claude Code session, which an agent cannot launch | control: G-D0 and orient make a missing target loud regardless; the owner runs the two probes (task log, CE-38 close)
- residual: G-D0 reds an adopted repo after an engine reinstall whose kit contract changed within the same major.minor | rung: collective | why: equality with the installed kit is what makes "the framework owns the file" mechanical | control: the red's remedy is one copy, the same step as the upgrade ritual (kit README § Upgrade)
F: changes when Claude Code changes how @-imports or SessionStart hooks load (the owner re-runs the live probes then), and every engine release that edits kit/contract.md makes each adopted repo copy it, which G-D0 enforces
A: by hand: manual-mode § init step 4 (append the bootloader, copy the contract, add the hook JSON from the kit README); G-D0's checks are a diff of two files and a look between the markers
M: one kit file per target (bootloader.md to CLAUDE.md, contract.md to docs/framework/contract.md); G-D0 compares both with the installed kit, so the shipped and the repo copy cannot drift silently
E: reuses the kit markers, init's create-only writes and seen-check, G-D0 and orient's sections; no new operation and no new config key
