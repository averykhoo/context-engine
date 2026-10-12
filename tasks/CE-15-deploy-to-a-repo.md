---
type: Task
id: CE-15
title: "Deploy path: how any repo gets the system, as text Claude Code manages"
brief: "Bootstrap (§6.9) and adoption (§11) after dogfooding here; no server the owner starts (anti-goal, DEC-10)"
pri: NOW
state: open
deps: [CE-8]
source: session 2026-10-08b
created: 2026-10-08
moved: 2026-10-11a
updated: 2026-10-12b
closed:
---

The owner: *"lets start with it in here and dogfood it, then we'll figure out how to adopt it in
new repos"* (US-9). After CE-8, design how a repo, new or existing, gets the system: what is
committed (`.mcp.json`, `context.toml`, ritual text in `CLAUDE.md`, skills), how the engine is
found from its own env, how a version upgrade lands (G-D0), and how existing repos map rather
than move (§11.4). Feeds CE-7 and CE-11.

## Traps

- Anti-goal: nothing the owner starts or manages by hand. Any server is started by Claude Code
  as a session ritual (charter G4).
- Never install the engine into a target repo's environment (CLAUDE.md, DEC-1).

## Read first

- `docs/framework/FRAMEWORK.md` §6.9, §8.0.2, §8.0.3, §10, §11
- `docs/decisions/DEC-10-charter-confirmed-whole-framework.md`

## Log

- 2026-10-09b (claude-code/claude-opus-5-5): DEC-16 (FRAMEWORK §6.6, several tasks -> one subagent each, top level only reports) must ship in the deployed contract text, so every framework repo gets it.
- 2026-10-09c (claude-code/claude-opus-5-5): DEC-17 (ultracode has standing approval when used to minimize token/context consumption) is now FRAMEWORK §6.6 'Ultracode'; the deployed contract text must carry it, like DEC-16.
- 2026-10-12a (claude-code/claude-opus-5-5): US-15 paste test (docs/evidence/framework-paste-test-2026-10-12.md): the kit must carry a context.toml schema or commented template, the install and version-pin step, ledger/HANDOFF/charter skeletons (first banner, empty-ledger key), a definition of the adopter's gate, and runbooks and FRAMEWORK without this repo's ids and paths. Ritual order itself is CE-24.
- 2026-10-12b (claude-code/claude-opus-5-5): build: 02973b6 FRAMEWORK deploy path de-leaked (6.9, 8.0, 10, 11.1, 11.4, leaks); a1e2cd3 adoption kit text at src/context_engine/kit/ and bootstrap.init (create-only), tests/test_kit.py + tools/sabotage_ce15.py (18 rows red). Next: init on CLI/MCP, config unknown-key refusal, first banner, after CE-23 commits the shared files.
- 2026-10-12b (claude-code/claude-opus-5-5): build landed: 02973b6 FRAMEWORK de-leak; a1e2cd3 kit + bootstrap.init; faf37ae init on CLI/MCP (no config needed), config refuses unknown [engine]/[working]/[kinds.*] keys, first banner via --seen none, package-data, Adoption kit route, manual-mode § init, AC-30..34 tested. Gate 228 passed, lint clean, tools/sabotage_ce15.py 31 rows red. Not done: shipping runbooks de-leaked (CE-24), no release tag (owner), G-D0 (CE-21).
- 2026-10-12b (claude-code/claude-opus-5-5): review-correctness: gate 228 green; sabotage_ce15 31/31 red re-run in an archive copy; wheel ships kit/. Must-fix: lint G-W1 now silent when sessions have closed but the note has no banner (find_banner returns None; working.py::Engine.lint_working 'if closes and b'). Should-fix: CLAUDE.md append separator untested; init refuses forever once context.toml is edited or run with other --prefix; unknown top-level tables/[working.caps] keys accepted.
- 2026-10-12b (claude-code/claude-opus-5-5): review fixes: G-W1 red when a session closed and the note has no banner; init never doubles an older kit block, keeps an existing context.toml that loads (BOM ok, --prefix must agree) and writes only what it points at; config refuses unknown top-level tables, unknown caps tiers and mistyped values; kit contract carries session start + orient, MCP optional (matches 11.1), says where FRAMEWORK/manual-mode live; skills sentence (10, kit README); shipping runbooks moved to CE-24 scope, CE-7 deps CE-24. sabotage_ce15 43 rows red.
