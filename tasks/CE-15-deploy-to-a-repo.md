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
review: [shipped, write-op, guard]
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

## Design review

affects: the session adopting a repo, the adopting repo's owner and its plain-git humans, the repo's own environment and files, the next session in that repo with no context, every repo the engine is pointed at
- eliminated: init installs the engine into the target repo's environment | rung: eliminate | control: bootstrap.init only writes text files and installs nothing; the kit README installs into the engine's own env (DEC-1)
- eliminated: init starts or registers a server the owner then manages | rung: eliminate | control: bootstrap.init registers no MCP server; the session runs `claude mcp add` (charter G4, DEC-10, DEC-25)
- eliminated: the kit text and the engine code that reads it come from different versions | rung: eliminate | control: the kit is package data beside bootstrap.py (pyproject package-data), so one install carries both
- reduced: init overwrites a file the repo already has | rung: reduce | control: bootstrap.plan is create-only, and keeps an existing context.toml once it loads (test_init_never_overwrites_and_a_second_run_is_a_no_op, test_init_keeps_an_edited_context_toml_and_writes_only_what_it_points_at)
- reduced: the CLAUDE.md append glues the contract to the last line, or doubles a block from an older kit | rung: reduce | control: bootstrap.plan's separator and ANY_BEGIN check (test_the_contract_block_starts_on_its_own_line_after_a_blank_one, test_an_older_kit_block_is_never_doubled)
- reduced: two kinds share an id prefix, or a --prefix override is malformed or names no kind | rung: reduce | control: bootstrap.config_text and config.from_dict refuse it (test_init_refuses_a_context_toml_that_does_not_load_and_bad_prefixes, test_a_prefix_override_lands_in_its_own_kind_only)
- reduced: a typo in an adopter's context.toml is silently ignored | rung: reduce | control: config.from_dict refuses unknown tables, keys, caps tiers and mistyped values (test_the_config_refuses_an_unknown_key_naming_the_allowed_ones, test_the_config_refuses_unknown_tables_tiers_and_mistyped_values)
- reduced: the kit carries this repo's ids or paths into another repo | rung: collective | control: test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths, in the gate
- reduced: the kit drifts from the engine (config template, empty ledger, FRAMEWORK §6.6 text) | rung: collective | control: test_the_config_template_names_every_key_the_engine_reads_and_parses, test_the_ledger_skeleton_is_the_engines_empty_ledger, test_the_kit_contract_carries_framework_6_6_verbatim
- reduced: a fresh repo's note has no banner, so a closed session goes unflagged | rung: collective | control: G-W1 is red when a session closed and the note has no banner (test_lint_g_w1_is_red_when_a_session_closed_and_the_note_has_no_banner); the first `banner set` needs --seen none
- residual: an adopted repo runs an engine whose major.minor no longer matches its committed `framework:` line or kit block | rung: individual | why: G-D0 is not built (CE-21), and the kit marker version in bootstrap.BEGIN is a literal not tied to __version__ | control: the kit README § 4 (Upgrade) steps and the pin in the first ledger summary; CE-21 makes it a lint check
- residual: adopters pin the engine by a bare commit SHA, because there is no release tag | rung: individual | why: cutting a release tag is the owner's call | control: the kit README § 1 (Install and pin) says to pin a full commit SHA until releases exist and to record the ref in the first ledger summary
- residual: the runbooks are not in the kit, and manual-mode.md still carries this repo's ids, so an adopter without the engine has no by-hand fallback on disk | rung: individual | why: de-leaking the runbooks so they can ship is CE-24's scope (CE-7 depends on it) | control: the kit README § Runbooks and the contract say where to read them (the engine repo at the pinned ref); CE-24
- residual: the kit's default prefixes collide with ids the adopting repo already uses outside the engine's record directories | rung: individual | why: the engine cannot see ids in files it is not pointed at | control: init's --prefix override and the context.toml.template comments on mapping an existing repo (FRAMEWORK §11.4, map rather than move)
- residual: a kit file added in a new subdirectory is not shipped in the wheel | rung: individual | why: pyproject package-data lists one glob per kit directory, and the gate does not build a wheel | control: whoever adds a kit directory adds its glob; the wheel was built and its kit/ checked by hand (CE-15 log)
- residual: a write that lands between init's plan and its write is overwritten | rung: individual | why: init runs before the repo has a context.toml naming a lock file, so it takes no lock, and the CLAUDE.md append is a read then rewrite | control: `init --dry-run` first; init runs once at bootstrap; git shows any overwritten tracked file
F: the kit changes whenever a config key, the empty ledger or FRAMEWORK §6.6 changes, by whoever changes them; the drift tests above go red when it goes stale, and a kit version bump moves bootstrap.BEGIN and the framework: line
A: the kit is plain text in src/context_engine/kit/, readable in the engine repo at the pinned ref; manual-mode.md § context-engine init and the kit README § 2b (Bootstrap by hand) do every init step without the engine
M: init only creates, so a re-run is a no-op; one schema (context.toml.template) checked against the config dataclasses; one marked contract block per CLAUDE.md
E: one new operation (`init`) with one name across library, CLI and MCP; the kit reuses this repo's own record layout and the engine's own empty ledger and banner rules
