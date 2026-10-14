# Framework sync audit, 2026-10-14

FROZEN. The audit as it ran in session 2026-10-14a; what was done about each finding is in CE-69 and the tasks named below.

Session 2026-10-14a ran a read-only audit across five dimensions, with one adversarial verifier per dimension (10 agents).
The gate was green before it ran: 635 passed, 2026-10-14. Every finding below survived verification ('partly' means the verifier narrowed it, and that narrowed claim is the one recorded here).
Where each finding went: CE-69 (sync sweep), CE-51, CE-70, CE-71, CE-72, CE-73, and comments on CE-47 and CE-56.

## kit-copies

### kit-copies/F1 (drift, confirmed)

Repo context.toml lacks two routes the 0.5 kit template ships: 'Framework contract' (docs/framework/contract.md) and 'Batons and pause records' (docs/working).

Evidence: `context-engine routes` (2026-10-14) lists neither path. The 'Frozen provenance' route's pattern `FRAMEWORK-v0.*.md` excludes contract.md. docs/working holds BTN-1..3. The template has `component = "Framework contract"` and `component = "Batons and pause records"`. The contract says "Where each component lives is `[[routes]]` in `context.toml`". Kit README § 4 step 2 asks upgraders to copy only "each new runbook's `[[routes]]` entry ... lint cannot tell that one is missing", and that gap is how these two were missed.

Fix: Add both [[routes]] blocks to the repo's context.toml. Change kit README § 4 step 2 to say 'copy every new [[routes]] entry', not only runbook ones (and change docs if mirrored).

### kit-copies/F2 (drift, confirmed)

Repo CLAUDE.md § Procedures 'Session start' still uses the pre-hook wording. Because CLAUDE.md overrides the contract, an agent following it after compaction or /clear runs session start again.

Evidence: CLAUDE.md: "**Session start:** `context-engine session start` (prints the key; use it as `CE_SESSION`), then `context-engine orient`." The contract (= kit/contract.md) says: "if you already hold one (after a resume, `/clear` or compaction), keep it, do not run `session start` again", and also "where they narrow or override a rule here, `CLAUDE.md` wins". The repo's .claude/settings.local.json already carries the orient hook.

Fix: Cut CLAUDE.md's Session start paragraph down to repo-only additions, or match the contract: the hook prints orient, and a session that already holds a key keeps it.

### kit-copies/F3 (drift, confirmed)

Repo CLAUDE.md § Rules tells agents to commit with plain `git commit -o`. The kit contract says to commit through `context-engine commit`, so uncommitted op-log lines go with the commit. CLAUDE.md wins, so the op lines get left behind.

Evidence: CLAUDE.md: "Commit by path (`git commit -o <paths>`); never `git add -A`, never `git stash`." Contract § Rules: "Commit by path, through `context-engine commit <paths> -m \"<message>\"` ... (a plain `git commit -o <paths>` only for paths no uncommitted op line names)".

Fix: Change the CLAUDE.md rule to `context-engine commit <paths> -m ...` and keep the never add -A / never stash clauses.

### kit-copies/F4 (drift, confirmed)

Kit manual-mode.md refers to 'the checked-in `.mcp.json`' and its `${CE_PYTHON}`. That file belongs to this repo only: the kit never ships it and init never writes it, so it leaks into every adopted repo. The LEAK test does not catch it.

Evidence: src/context_engine/kit/docs/runbooks/manual-mode.md § When the MCP tools are missing: "so the checked-in `.mcp.json` stays machine-neutral. Its `${CE_PYTHON}` works only if the variable was in Claude Code's starting environment". bootstrap.py::FILES has no .mcp.json. FRAMEWORK §10: ".mcp.json # optional, not committed by default". Only this repo tracks .mcp.json, with `"command": "${CE_PYTHON}"`. tests/test_kit.py::LEAK only matches ids, spike/, tools/sabotage and machine paths.

Fix: Reword it generically, e.g. 'so no machine path is checked in; a repo that keeps a .mcp.json ...'. Copy the result to docs/runbooks/manual-mode.md so the AC-37 byte-equality still holds.

### kit-copies/F5 (nit, confirmed)

Kit manual-mode 'Record kinds (the kit's defaults)' table gives the baton/pause mode as `session-stamped`, but the config value is `stamped`. It also leaves out list keys that the template types.

Evidence: manual-mode.md table: "| baton | `BTN-n` | `docs/working` | session-stamped |". Template: `mode = "stamped"`. config.py::CHANGE_MODES = ("append-only", "replaced", "stamped"), and any other value is refused. The table also leaves out the task/question `review` list and the decision lists tags, relaxes, narrowed_by, creates, amends, retires, tasks, code and refs.

Fix: Write `stamped` in the Mode column (session-stamped can go in prose), and add the missing list keys or point to the template for them. Update both copies.

### kit-copies/F6 (nit, confirmed)

The kit template has no route for the residual-risk register, so in an adopted repo `context-engine routes` never says where the register lives.

Evidence: context.toml.template sets `[working] register = "docs/invariants.md"`, and FRAMEWORK §10 lists `invariants.md # the residual-risk register`. The repo's own config routes it as 'Residual-risk register', but the template's [[routes]] has no entry for it.

Fix: Add an `optional = true` [[routes]] entry for docs/invariants.md to the template, as is done for ops.jsonl.

### kit-copies/F7 (nit, confirmed)

Guard gap: nothing checks the kit README's file table or its list of directories init creates against bootstrap.py::FILES and KEEP. They agree today, but a new kit file would leave the README stale without any test failing.

Evidence: kit/README.md has a table headed '| Kit file | Goes to | What it is |' with 13 rows, and the line "`init` also ... creates `docs/decisions/`, `docs/stories/`, `docs/working/`, `docs/evidence/` and `tasks/`". The only README checks in tests/ are for the '## Hook' and '## 4. Upgrade' headings (tests/test_kit.py).

Fix: Add a test in tests/test_kit.py that parses the table's first column and checks it equals FILES keys plus {TEMPLATE, BOOTLOADER, CONTRACT}, and checks the directory list equals KEEP. Sabotage it once to see it fail.

### kit-copies/F8 (nit, confirmed)

This repo has no .claude/.gitignore. settings.local.json, which holds machine paths and the hook, is ignored only by the user's global git ignore.

Evidence: `git check-ignore -v .claude/settings.local.json` matches only C:/Users/user/.config/git/ignore:1. The root .gitignore has no claude entry. bootstrap.py::_check_ignore would flag this case ("it does not ignore settings.local.json ... add that line").

Fix: Add .claude/.gitignore containing `settings.local.json`, which is what init writes.

Checked and consistent:

- 6 runbooks in docs/runbooks are byte-equal to their kit copies (cmp). Guarded by tests/test_kit.py::test_the_kit_runbooks_are_this_repos_runbooks (AC-37).
- docs/framework/contract.md is byte-equal to kit/contract.md. The CLAUDE.md kit block is byte-equal to the kit/bootloader.md block, with no CR in either. Both are guarded by lint G-D0 (working.py::lint_contract), which runs inside the gate. `context-engine lint` is clean.
- `framework: 0.5` appears in bootloader.md, kit/contract.md, the repo's contract and CLAUDE.md. The marker reads `kit 0.5`. __version__ 0.5.0.dev0 matches the pyproject version (tests/test_version.py).
- The kit ledger skeleton equals EMPTY_LEDGER (test). Template keys are checked against the config dataclasses, and template provenance against G-D9 (test).
- Every `context-engine <group> <verb>` cited in kit files exists in the CLI. Every cited --flag is either an engine flag or a git/claude flag. The init flags in the README (--prefix, --dry-run, --merge-settings, --skip-settings) match init --help.
- The MCP tool mapping in procedures.md (hk_expire_batons, hk_regen_index, init, why) matches the server's tool list.
- Every FRAMEWORK § number, P-number and named § section cited by kit files exists. §4.1 is the OKF spec's. Guard ids cited exist in config.py or FRAMEWORK.
- Kit files cite no repo ids (CE/DEC/US/AC/INV-n) and no machine paths. Example ids use the kit's own prefixes.
- pyproject package-data `kit/**/*` with setuptools>=68 ships the nested docs/runbooks and docs/ledger. Guarded by test_the_wheel_carries_every_kit_file.
- bootstrap.py::FILES, KEEP and SELF_IGNORING agree with the kit README and FRAMEWORK §10. The e2e test's expected `init: created 22` checks out arithmetically.
- The pytest marker string in kit criteria.md matches pyproject markers. The template claim regex matches both claim forms.
- Runbook frontmatter carries `mode: replaced` and `liveness: LIVING`, as FRAMEWORK §7.5 requires.
- Anchors in procedures.md/manual-mode.md and named § references (README § Hook, § Upgrade, manual-mode § When the engine and this runbook disagree) exist. Lint link guard is clean.
- The bootstrap steps in procedures.md and README §2a/§2b agree with FRAMEWORK §6.9 steps 1-5.
- The repo's .claude/settings.local.json carries the orient SessionStart hook.

## spec-vs-engine

### spec-vs-engine/F1 (drift, confirmed)

Several guards are described in the spec in the present tense, with no *Not built yet* marker, but have no implementation: G-T4, G-T7, G-W9, G-W10, G-W11, G-V2 and G-V3.

Evidence: FRAMEWORK.md lines 5-7 promise that unbuilt parts say *Not built yet* and name the task. Only G-T5 (CE-34) and G-V1 (CE-17) carry that marker. The guards.py module docstring says: "Not here ...: G-T5 mutation per criterion, G-T4 structural anchors, G-T7 deviations, G-W9 to G-W11 (housekeeping), G-V1 to G-V3". §8.4 G-W9 says "`hk.close` checks it at write time; the lint re-checks it in the stored files", but neither exists. The implemented set, from config.py's known-guard list, is G-D0..12, R1, I1, I2, T1, T2, T3, T6, W1..W7, W12, W13. The coverage map docs/evidence/framework-coverage-2026-10-12.md marks these DEFERRED or owned by CE-6 / CE-17.

Fix: Add *Not built yet (CE-n)* or 'deferred' to G-T4 (§3.4, §8.2), G-T7 (§3.5, §8.2), G-W9, G-W10 and G-W11 (§8.4), and G-V2 and G-V3 (§8.5).

### spec-vs-engine/F2 (drift, confirmed)

The spec names the section-replace operation `section.set`, but the engine calls it task_section (MCP `task_section`, CLI `task section`). There is no `section_set` tool.

Evidence: §5.2 "(`section.set`)", the §8.0.1 table "set one section at a time (`section.set`)", and the §8.0.2 Tasks row "`section.set(id, name, text)`". The spec's own naming rule maps that to `section_set`. The operation that exists is ops.py::task_section.

Fix: Write `task.section(id, name, text)` in all three places.

### spec-vs-engine/F3 (drift, confirmed)

Several operation signatures in the spec use parameter names that differ from ops.py. The MCP tool schemas are built from the ops.py parameters, so an agent following the spec passes wrong argument names.

Evidence: mcp.py::make_tool builds each schema from ops.Op.params. The mismatches: §5.4 `pause.open(in_flight, resume_step, ...)` vs ops.py::pause_open(in_flight, resume, ...). §5.3 `ask.answer(id, owner_words)` vs ops.py::ask_answer(id, words, title), where title is required. §5.1, §5.5 and §8.0.2 `banner.set(text, seen_hash)` vs ops.py::banner_set(text, seen). §8.0.2 `session.close(summary, rows, receipts, owed)` vs ops.py::session_close(rows, summary, guards, read, asked, owed). §8.0.2 `lint(scope)` vs ops.py::lint(working: bool).

Fix: Change the spec signatures to the engine's parameter names (resume, words + title, seen, guards/read/asked, working).

### spec-vs-engine/F6 (drift, confirmed)

The engine does not enforce the standard id form `[A-Z]+-[1-9][0-9]*` on prefixes. init accepts digits and its remedy even suggests T2, and a hand-edited config accepts any non-empty prefix.

Evidence: P3 says the prefixes are per-repo config but "the form is not". bootstrap.py::PREFIX_RE is `^[A-Z][A-Z0-9]*$`, and the bootstrap.py::config_text remedy says "write it like D, DEC or T2". config.py::from_dict checks only that a prefix is non-empty and unique. An in-memory, read-only probe: prefix "ce_2" loads, and Kind.id_re becomes `^ce_2-(\d+)$`. No lint failure follows.

Fix: Validate prefix against ^[A-Z]+$ in config.py::from_dict and in bootstrap.py::PREFIX_RE, and remove 'T2' from the remedy.

### spec-vs-engine/F10 (drift, confirmed)

§9.3.1 says G-W4 checks that the state key and `status` agree for decisions, stories and the charter. G-W4 actually checks board items only, and no guard checks decisions.

Evidence: §9.3.1: "Decisions use `decision_status`, stories `story_status`, the charter `charter_status`. G-W4 checks the two keys agree." The G-W4 loop in working.py::Engine.lint_working iterates self.board_heads() only. Stories are covered by G-I2 (guards.py::retire_problems). For decisions, nothing checks that SUPERSEDED matches `status: deprecated`, so a hand-set `status: deprecated` on a BUILT decision passes lint, and guards.py::_deprecated then makes G-D3 and G-T3 skip it as history. No code reads `charter_status`.

Fix: Change §9.3.1 to 'G-W4 for board items, G-I2 for stories'. Either add a decision check (SUPERSEDED iff deprecated) or mark it not built, and say that the charter key is unchecked.

### spec-vs-engine/F9 (drift, partly)

With the default config, lint does resolve links in Read first through G-D3. The "floor on how many there are" is unbuilt and has no marker.

Evidence: §5.2: "`## Read first`, whose pointers lint resolves, with a floor on how many there are". Only working.py::Engine.orient (for display) and working.py::TASK_BODY ("## Read first\n\n- none yet") touch that section. Pointers are resolved only incidentally, by G-D3, when the board directory is listed in [guards] links.

Fix: Mark the floor *Not built yet (CE-n)* or drop it, and say that pointer resolution is G-D3's when the board is listed.

### spec-vs-engine/F11 (drift, confirmed)

The §9.3 OKF profile claims two features that have no code and no *Not built yet* marker: a generated log.md concept changelog, and refusal of an expired stale_after.

Evidence: §9.3: "`log.md` | **generated** from decisions' `creates/amends/retires`" and "**our profile refuses** an expired `stale_after` on a live item". `stale_after` appears nowhere in src/context_engine/, and log.md appears only in store.py::RESERVED_MD.

Fix: Mark both *Not built yet (CE-n)*.

### spec-vs-engine/F12 (drift, partly)

This is a nit: the deferred deviation register has no specified type, prefix or required keys, and no runbook step, so an adopting repo must invent them. The engine would enforce append-only for it once declared.

Evidence: §8.0.1 table: "**append-only** | decisions, stories, deviations"; §3.5 Deviation register. Neither context.toml nor src/context_engine/kit/context.toml.template has a [kinds.deviation] table. The only mentions in code are guards.py::CRITERION_STATUSES ('deviates') and the guards.py docstring's 'G-T7 deviations' under Not here. The coverage map row says G-T7 is DEFERRED until the deviation register exists.

Fix: Mark the deviation kind and G-T7 as not built or deferred, or add a commented [kinds.deviation] to the kit template.

### spec-vs-engine/F4 (nit, confirmed)

The mcp.py and working.py module docstrings say the hk_ operations other than baton expiry are not exposed or not handled. hk_regen_index is both exposed and implemented.

Evidence: The mcp.py docstring says "Deliberately not here: the ``hk_`` operations other than ``hk_expire_batons`` (CE-6)", yet mcp.py::server registers every op, including ops.py::hk_regen_index, which is live as mcp__context-engine__hk_regen_index. The working.py docstring says the hk_ ops other than baton expiry are not handled, but working.py::Engine.reindex implements one, and it still says '(in CE-3, the MCP server)'.

Fix: Change both docstrings to 'other than hk_expire_batons and hk_regen_index'.

### spec-vs-engine/F5 (nit, confirmed)

The §8.0.2 operation table, which claims to list the MCP surface, omits `init` and `register.show`, although both exist.

Evidence: ops.py::init and ops.py::register_show are exposed as CLI commands and MCP tools. Both are described elsewhere in the spec (§6.9 and §7.4) but are missing from the §8.0.2 Group | Tools table.

Fix: Add an Adoption row (`init`) and a Register row (`register.show(engine)`).

### spec-vs-engine/F7 (nit, confirmed)

P3 says every id prefix is per-repo config, but the goal (G) and register (INV) prefixes are hard-coded.

Evidence: guards.py::GOAL_RE is `G-?([1-9][0-9]*)` and review.py::_ENTRY is `^## (INV-(\d+)):`. Neither goals nor register entries are kinds, so `[kinds.*].prefix` cannot change them.

Fix: State in P3 that G-n and INV-n are fixed by the framework, or make them configurable.

### spec-vs-engine/F8 (nit, confirmed)

The spec's own normative decision example uses an id that breaks the standard form it mandates. Copying the example into a `decision link` would be refused.

Evidence: §6.5 YAML: "tasks: [TK96]". working.py::Engine.link refuses targets outside the configured series. The kit's task prefix is T.

Fix: Change it to `tasks: [T-96]`.

### spec-vs-engine/F13 (nit, confirmed)

The spec gives two different shapes for `verified` (a mapping vs a list), and no code settles which.

Evidence: §6.5: "verified: { by: human:owner, at: ... }"; §9.3: "`verified: [{by: human:owner, at}]`". working.py::DECISION_OWNED refuses writes to verified, so the engine never writes either shape.

Fix: Pick one shape and use it in both places.

### spec-vs-engine/F14 (nit, partly)

Ledger rotation and the `abandoned` writer are unbuilt and unmarked in §7.1. The `foreign` entry is written by hand under procedures.md, as designed.

Evidence: §7.1: "Rotate by period when it passes its cap", and `abandoned` / `foreign` entries. The ledger.py docstring says "Deliberately not handled: rotating the ledger by period". The working.py docstring says marking a stub `abandoned` is not handled (CE-6). ledger.py::KINDS parses both kinds, but no operation writes either.

Fix: Mark these *Not built yet (CE-6)*.

### spec-vs-engine/F15 (nit, confirmed)

§8.0.2's naming example uses `hk_close`, an MCP tool that does not exist.

Evidence: "MCP tool names use underscores (`session_start`, `task_close`, `hk_close`)", while the same section says hk.close is "not built yet, CE-6".

Fix: Use `hk_expire_batons` in the example.

### spec-vs-engine/F16 (nit, confirmed)

§8.0 says every guard docstring states what it deliberately does not check. Four guard entry points do not.

Evidence: working.py::Engine.lint_working (G-W1..W6) has no docstring at all. working.py::Engine.lint_routes (G-R1), store.py::Store.lint_bundles (G-D11) and store.py::Store.body_problem (G-D10) have docstrings without a not-checked clause. Every guards.py guard and Engine.lint_contract does have one.

Fix: Add the 'Not checked:' clauses to these four.

### spec-vs-engine/F17 (nit, confirmed)

The spec cites closed CE tasks as provenance, against its own rule that a CE-n is a build-status marker. One UNVERIFIED claim points at a closed task.

Evidence: Line 47: "A `CE-n` in parentheses ... is build status". 11 of the 16 cited CE ids are closed (13, 19, 20, 21, 22, 26, 30, 31, 32, 35, 38). §8.0.2 says "(UNVERIFIED, CE-13)", but CE-13 is closed and its log points at spike/FINDINGS.md row 5.

Fix: Drop the citations of closed tasks, and point the CE-13 one at spike/FINDINGS.md.

Checked and consistent:

- CLI <-> ops.OPS <-> MCP parity: set(cli.CLI_OPS.values()) == set(ops.OPS), and every op parameter has a CLI dest (in-memory probe); mcp.py::server registers every op; tests/test_mcp.py pins this
- Every CLI spelling the spec names exists in cli.py (task/ask/baton/pause/record/decision/session/banner/register/init/lint/commit/why/orient/routes)
- §8.0.2 hk row: `baton expire` = hk_expire_batons and `decision index` = hk_regen_index; hk.comment/stamp/ratchet/close are marked not built and are absent from the code
- §5.5 rule 4 milestone list == the methods working.py decorates with _milestone, plus pause_open's own commit; [engine] commit policies == config.py::COMMIT_POLICIES
- §6.5 decision.set refusals == working.py::DECISION_OWNED; the decision_status enum matches §6.5
- §5.3: ask_answer reports unblocked items (deps + blocks); task close refuses a question; overdue = 5 sessions / 7 days
- §6.1 orient contents == working.py::Engine.orient sections
- G-D0 behaviour (0.5.* synonym, kit block, contract equality, orient opens with failures) == working.py::Engine.lint_contract
- Guard ids in config.py's known list are all implemented; G-T5 and G-V1 are correctly marked not built; G-M1 is built via tests/test_repo_records.py; G-W8 is a write-time refusal
- [kinds.*] in context.toml and the kit template: no kind stores state in `status`; store.py::OKF_STATUS enforces draft/stable/deprecated; story enums match §3.2; caps NOW 1 / NEXT 5, max_pauses 2, baton_max_age 2
- Id reading is deliberately loose (Kind.id_re reads legacy ids as written, P3); G-D2 checks duplicate files and duplicate creates in the op log
- Read-only `context-engine lint` on the repo: 'lint: clean' (2026-10-14)
- The spec holds no repo DEC/US/AC/INV ids (ASK-12 appears only in the illustrative §6.5 example)

## runbooks-vs-cli

### runbooks-vs-cli/F1 (drift, confirmed)

manual-mode § context-engine init (step 3 and its Why) lists only manual-mode.md and procedures.md as the runbooks init copies. init actually copies all six, including gate, sabotage, fan-out and release.

Evidence: docs/runbooks/manual-mode.md § init step 3: "Copy `HANDOFF.md`, ... `docs/runbooks/manual-mode.md` and `docs/runbooks/procedures.md` from the kit"; Why: "the two runbooks included". Code: src/context_engine/bootstrap.py::FILES also maps docs/runbooks/gate.md, sabotage.md, fan-out.md and release.md.

Fix: In step 3, list all six runbooks (or say 'every file under kit/docs/runbooks/'), and change the Why from 'the two runbooks' to 'the runbooks'. Edit the kit copy too, so the two copies stay byte-equal.

### runbooks-vs-cli/F2 (drift, confirmed)

manual-mode § session start says that if HANDOFF.md exists without a `## Banner (<key>)` heading, session start, orient and both banner commands refuse. The code does not refuse, and the same runbook's § banner show / banner set describe the no-heading case as a normal 'none' hash.

Evidence: manual-mode.md § session start: "if it exists it must have a `## Banner (<key>)` heading: without one, session start, orient and both banner commands refuse." vs § banner show: "If the orientation note (`HANDOFF.md`) has no `## Banner (<key>)` heading yet ... the hash is `none`." Code: ledger.py::find_banner returns None. working.py::Engine.session_start, Engine.orient ('no banner'), ops.py::banner_show ('no banner yet ... --seen none') and Engine.banner_set (first banner) all go ahead. Only ledger.py::read_banner refuses, and no operation calls it directly.

Fix: Delete the refusal sentence in § session start. Replace it with: 'with no heading yet, the banner key does not count, and `banner show` gives hash `none`'. Edit the kit copy too.

### runbooks-vs-cli/F3 (drift, confirmed)

The Intake procedure and CLAUDE.md say to pass owner words from a file, not a heredoc. But `record amend` and `ask answer` take the words only as a command-line argument, so two of the four intake commands cannot follow that rule from the CLI.

Evidence: procedures.md § Intake row 1: "Write the words to a file with an editor, not a shell heredoc" ... "`context-engine record amend <id> "<words>"`; ... `context-engine ask answer <id> "<words>" --title`". CLAUDE.md § Procedures: "Write owner words to a file with the Write tool, not a heredoc". cli.py::build gives --file only to `record new` and `record retire` (and banner set). `record amend` takes positionals id and text; `ask answer` takes id and words plus --title.

Fix: Add `--file` (mutually exclusive with the positional) to `record amend` and `ask answer`. Or note in the Intake row that for these two the CLI needs the words quoted on the command line, and that the MCP tools are preferred.

### runbooks-vs-cli/F4 (drift, confirmed)

CLAUDE.md § Rules says to commit with plain `git commit -o <paths>`. The framework contract, procedures.md and manual-mode say to commit through `context-engine commit`, and warn that a plain `git commit -o` of a record whose op line is uncommitted fails G-W7 on a clean checkout. The contract says CLAUDE.md wins where it overrides.

Evidence: CLAUDE.md § Rules: "Commit by path (`git commit -o <paths>`); never `git add -A`, never `git stash`." docs/framework/contract.md § Rules: "Commit by path, through `context-engine commit <paths> -m "<message>"` ... (a plain `git commit -o <paths>` only for paths no uncommitted op line names)". procedures.md § Clean close row 7 Why: "a plain `git commit -o` of a record whose op line is still uncommitted fails lint on a clean checkout (G-W7)". The safe path is working.py::Engine.commit.

Fix: Reword CLAUDE.md § Rules to: "Commit by path through `context-engine commit <paths> -m ...` (plain `git commit -o` only for paths no uncommitted op line names); never `git add -A`, never `git stash`."

### runbooks-vs-cli/F5 (drift, confirmed)

CLAUDE.md puts `Closes: CE-n` on the agent's own commit. The procedure, manual-mode and the code put it on the engine's task-close commit, made after the work is committed, and recent history follows the procedure.

Evidence: CLAUDE.md § Rules: "Every agent commit ends with a `Session: <key>` trailer, plus `Closes: CE-n` when it finishes the task." procedures.md § Clean close row 4: "the close's commit carries `Closes: <id>`". manual-mode § task close: "one trailer paragraph, `Closes: <id>` and `Session: <key>`". working.py::Engine.close sets commit_trailers = ["Closes: <id>"]. git: 0f1d071 (CE-68 work) has no Closes; f8a19b4 (CE-68: close) has Closes: CE-68. If an agent also writes Closes by hand, the procedures § Housekeeping step that closes items named by Closes: trailers would then try to close an item that is already closed.

Fix: Change CLAUDE.md to: "... ends with a `Session: <key>` trailer; `Closes: CE-n` is added by `task close`, which commits the close once the work is committed."

### runbooks-vs-cli/F6 (nit, confirmed)

CLAUDE.md and contract.md give a different session-start order from procedures.md, which says the order lives only there. They put 'do the batons' before 'show the other open sessions', while procedures.md puts it after. Neither mentions the start-of-session housekeeping row (stale stubs, foreign commits).

Evidence: procedures.md § Session start rows: session start -> Housekeeping at session start -> orient -> show other open sessions -> do batons/pauses -> raise + `ask raised` -> `task show`. CLAUDE.md § Procedures: "Do the batons and pause records it lists first. Show the owner the other open sessions...". contract.md § Procedures: "Do the batons and pause records it lists first, show the owner the other open sessions it lists...".

Fix: Make them agree. Preferred: reword CLAUDE.md and contract.md (kit/contract.md too) to 'show the owner the other open sessions, then do the batons...', since the owner may need to stop a session before work starts. Also add a pointer to procedures § Housekeeping (at session start).

Checked and consistent:

- Every `context-engine ...` command in procedures.md, manual-mode.md, gate.md, sabotage.md, fan-out.md, release.md, CLAUDE.md and contract.md exists in cli.py::build/CLI_OPS, and the flags and positionals shown parse. `--help` exited 0 on 10 sampled subcommands. A script checked that every op's parameters in ops.OPS are supplied by the parser.
- The MCP naming rule in procedures.md (group_verb, except hk_expire_batons and hk_regen_index) matches the names in ops.py.
- The milestone list in manual-mode 'Commit the write' matches the @_milestone ops in working.py (session_close, session_pause, close, ask_answer, baton_add, record_new, amend, retire, supersede, banner_set), plus pause_open's commit_always.
- The op-log line shape in manual-mode matches store.py::Store._log. Per-op fields spot-checked: new, close, ask.raised, session.*, banner.set, stamp, amend, register.append ordering.
- session start: key minting matches ledger.py::next_key/newest and the stub matches render_open. The close and pause entry layouts match render_close/render_pause (100-column wrap, 'nothing' default, asked line omitted when empty), and the asked-receipt check matches Engine.session_close.
- task new: frontmatter order and the TASK_BODY template match. task close: log line, title '<id>: close; <msg>' cut to 72 (commit.TITLE_MAX), and the Ops:/body/Also-carries/Closes+Session trailer order (commit.py::message) all match.
- ask raised stub-line rewrite, the ask answer decision (fields, body, answered map, unblocked report), baton add fields and body, and pause open (fields, porcelain read, commit title, always committed) all match manual-mode.
- baton expire task shape and its default actor process:housekeep (ops.py::hk_expire_batons), banner set hash and first-banner insertion (ledger.py::replace_banner), record new filling of date/key fields and story checks, and record stamp all-or-none all match.
- The by-hand steps in manual-mode § context-engine commit match commit.py::session_message and the refusals in Engine.commit.
- The kit-defaults table in manual-mode matches the kinds in kit/context.toml.template. Config defaults match: orient 6000 bytes, NOW 1 / NEXT 5, overdue after 5 sessions or 7 days, baton age 2.
- All six docs/runbooks/*.md are byte-equal to their kit copies, and docs/framework/contract.md equals kit/contract.md. `context-engine lint` is clean (2026-10-14).
- tools/linux_gate.py exists and takes an optional [rev] (default HEAD). tools/sabotage_ce2.py exists and sets PYTHONPYCACHEPREFIX, as CLAUDE.md says.
- The anchors procedures.md#push-and-ci-68 and #clean-close-63 match GitHub slugs. The item numbers in FRAMEWORK §6.3 match the § column of procedures.md § Clean close.
- The Push and CI steps in procedures.md agree with contract.md § Rules and CLAUDE.md § Gate (ask first, gate, watcher keyed on the hash, watch only, linux_gate before push).
- The SessionStart orient hook described in the contract is present in .claude/settings.local.json (gitignored).

## records-state

### records-state/F10 (drift, confirmed)

The HANDOFF banner nearly fills orient's 6000-byte cap. orient therefore drops the whole Board NOW/NEXT section and the top item's Traps, and cuts the banner itself.

Evidence: Measured 2026-10-14: `context-engine orient` printed 5990 bytes and the HANDOFF § Banner body is 5431 bytes. orient prints '## Board: NOW and NEXT\n[cut at the orient cap; the rest: `context-engine task list`]' and 'Traps:\n[cut at the orient cap; the rest: `context-engine task show CE-7`]'. HANDOFF step 2 promises orient shows 'the NEXT tier, ... the top item's Traps and Read first, under 6000 bytes'. context.toml's own provenance reads 'orient_max_bytes = 6000 # ... wrong if a routine orient gets cut'. No guard caps the banner's size: G-D8 only checks for stacked banners (guards.py, 'G-D8 the orientation note's stacking check').

Fix: Trim the banner, since much of it repeats CLAUDE.md or the contract (delegation, owner rules, push, CLI form). Then add a banner byte budget, or make orient reserve room for the board and the top item before the banner.

### records-state/F4 (drift, confirmed)

CLAUDE.md's commit rule says `git commit -o`. The contract and HANDOFF say `context-engine commit`, and the contract also says CLAUDE.md wins where it overrides.

Evidence: CLAUDE.md § Rules: 'Commit by path (`git commit -o <paths>`); never `git add -A`, never `git stash`.' contract.md § Rules: 'Commit by path, through `context-engine commit <paths> -m "<message>"`, which takes the op lines still uncommitted ... (a plain `git commit -o <paths>` only for paths no uncommitted op line names)'. contract.md: 'where they narrow or override a rule here, `CLAUDE.md` wins'. HANDOFF banner (CE-45, CE-55, DEC-36): 'Commit your own work through `context-engine commit <paths> -m ...`'.

Fix: Change CLAUDE.md's rule to `context-engine commit <paths> -m ...`, or drop it and defer to the contract. Do it now rather than under CE-47, which is LATER.

### records-state/F11 (drift, confirmed)

README.md, the public front page, says nothing is usable and lists a housekeeping script that does not exist.

Evidence: README.md: 'exposes them through a CLI, a per-session MCP server, and a no-model housekeeping script.' and 'Status: pre-alpha. Nothing here is usable yet.' Against that: CE-8 (engine runs this repo), CE-15 (init deploys the kit) and CE-10 (CI) are closed, while CE-6 (housekeeping script) is open LATER. src/context_engine/ has no script, only the hk_ aliases in cli.py. README also says 'pause blocks' where context.toml has [kinds.pause] records, and it gives no pointer to the install guide at src/context_engine/kit/README.md.

Fix: State what works now (CLI, MCP, lint, init), mark the housekeeping script as planned (CE-6), and link the kit README for install.

### records-state/F12 (drift, confirmed)

src/context_engine/REGISTER.md ships with the engine but still cites `rituals.md` and 'rituals §' sections. No such runbook exists since DEC-39/CE-68, and the ritual-ban test does not cover REGISTER.md.

Evidence: REGISTER.md INV-35 control: 'rituals.md § Intake steps 5 and 6 and the census evidence doc'. Other entries: 'rituals § Foreign reconcile' (x2), 'the contract and rituals name `context-engine commit`', 'the upgrade ritual (kit README § Upgrade)'. docs/runbooks/rituals.md and kit/docs/runbooks/rituals.md do not exist (procedures.md does). tests/test_kit.py::test_no_living_framework_text_says_ritual covers only FRAMEWORK, contract.md, CLAUDE.md, HANDOFF.md and kit files.

Fix: Point those controls at procedures.md (file a task if the 'edited only when the code changes' route rule forbids a hand edit), and add REGISTER.md to the test's file list.

### records-state/F1 (drift, confirmed)

HANDOFF's 'Next session: start here' step 3 names CE-3, which is closed, as the top item. The real top item is CE-7.

Evidence: HANDOFF.md: '3. `context-engine task show CE-3` (the top item).' tasks/CE-3-mcp-server.md has 'state: closed'. task list shows 'NOW CE-7', and the banner says 'NOW CE-7'. orient shows 'Top item: CE-7'.

Fix: Say 'the top item orient names' with no id, or update it to CE-7.

### records-state/F2 (nit, confirmed)

The banner's done list leaves out CE-4 and CE-9, both closed as done.

Evidence: Banner: 'CE-1..3, CE-5, CE-8, CE-10, CE-14..16, CE-20..26, CE-30..33, CE-35..38, CE-45, CE-49, CE-55, CE-67 and CE-68 done.' CE-4 closed 2026-10-11a (baseline in docs/evidence/adhoc-baseline-2026-10-11.md). CE-9 closed 2026-10-11c (FRAMEWORK trimmed, v0.5 archived). CE-13 and CE-19 were closed as not needed, so leaving those out is correct.

Fix: Add CE-4 and CE-9.

### records-state/F3 (nit, confirmed)

The banner's range of agent-drafted, unread criteria predates CE-67, so it leaves out AC-79 and AC-80.

Evidence: Banner: 'AC-60..64 and AC-71..78 are agent-drafted criteria the owner has not read.' That line came from banner 2026-10-13c (e5275f7). CE-67 (4febc25) then added AC-79 and AC-80 under docs/criteria.md '## CI parity (CE-67)', from US-18. The 13e banner did not extend the range.

Fix: Write 'AC-71..80', or confirm the owner read AC-79/80.

### records-state/F5 (nit, confirmed)

A HANDOFF fact still attributes G-T5 to CE-14. CE-14 split it out to CE-34.

Evidence: HANDOFF § Facts: 'Its 13 red results stand as CE-1's evidence; CE-14's G-T5 replaces both tables.' The CE-14 close note says 'G-T5 to CE-34', and CLAUDE.md says 'G-T5 (mutation per criterion, CE-34)'.

Fix: Change it to 'CE-34's G-T5'.

### records-state/F6 (nit, partly)

The line is time-bound and probably stale, and it adds to F10's overflow. It cannot be shown to be a dead condition: it stays true for any Claude Code process started before 13c.

Evidence: Banner: 'The MCP server (CE-3): one started before 2026-10-13c refuses every call here (the new `[guards]` keys): the owner restarts Claude Code; until then, the CLI.' Sessions 13d and 13e have run since then, so any server started now is newer. The line also adds to F10's overflow.

Fix: Drop it, or reword it as a general rule (a server older than the config's keys refuses; restart Claude Code).

### records-state/F13 (nit, confirmed)

CLAUDE.md is exactly at its G-D1 line cap, so the next rule added turns lint red.

Evidence: On 2026-10-14, `wc -l CLAUDE.md` gives 140 lines and 9483 bytes. The context.toml Contract route has 'max_lines = 140 # ... MEASURED 2026-10-12d, 116 lines, plus room for two or three rules; wrong if a rule that belongs here is kept in HANDOFF to stay under it'.

Fix: Trim CLAUDE.md (CE-47), or re-measure and raise the cap with fresh provenance.

### records-state/F8 (nit, confirmed)

CLAUDE.md's id-prefix list leaves out the BTN, PAU and G-n prefixes the repo mints.

Evidence: CLAUDE.md: 'tasks `CE-n`, decisions `DEC-n`, stories `US-n`, criteria `AC-n`, owner questions `ASK-n`, residual-risk register entries `INV-n`'. context.toml has [kinds.baton] prefix = "BTN" (docs/working/BTN-1..3 exist) and [kinds.pause] prefix = "PAU", and the charter goals are G-n (DEC-33).

Fix: Add BTN-n, PAU-n and G-n, or point at [kinds.*] in context.toml. CE-56 will rename them anyway.

### records-state/F9 (nit, confirmed)

The tools/ route describes the directory as sabotage evidence awaiting replacement, but it also holds tools/linux_gate.py, which CLAUDE.md requires before every push. The CI workflow and tests/ have no route.

Evidence: context.toml route 'Sabotage probes': path = "tools", pattern = "sabotage_<task>.py", mode = "kept as evidence until G-T5 replaces them (CE-34)". git ls-files tools also shows linux_gate.py, count_context.py and check_decision_import.py. CLAUDE.md § Gate: 'Before every push, also run CI's job on Linux here: `<interpreter> tools/linux_gate.py`'. .github/workflows/gate.yml has no route.

Fix: Add a 'Tools' route for linux_gate.py and the others, and a 'CI workflow' route for .github/workflows/gate.yml.

### records-state/F7 (nit, confirmed)

context.toml's header comment calls the routing table CLAUDE.md's and says the records are kept by hand.

Evidence: context.toml lines 1-2: 'the record kinds below describe the records this repo already keeps by hand (CLAUDE.md routing table).' Its own routes comment says 'Moved here from CLAUDE.md in CE-8', and CLAUDE.md says 'Engine mode since 2026-10-08f (CE-8)'.

Fix: Reword it to 'the records this repo keeps through the engine'.

### records-state/F14 (nit, confirmed)

The banner says guards.py runs G-D0, but G-D0 is in working.py. The line also reads as if it lists every lint guard.

Evidence: Banner: '`src/context_engine/guards.py` runs G-D0..D5/D7/D8/D9/D12, G-I1/I2, G-T1/T2/T3/T6 and G-W7 in lint'. guards.py's Failure ids start at G-D1. working.py has '# G-D0 (DEC-23): the engine is major.minor.patch'. Lint also runs G-D6, G-D10 (okf.py), G-D11, G-R1 and G-W*.

Fix: Start the guards.py range at G-D1 and add 'plus G-D0/D6/D10/D11, G-R1, G-W* elsewhere'.

Checked and consistent:

- lint: `lint: clean` rc=0 (2026-10-14); task list read (NOW CE-7, NEXT CE-64)
- every DEC/US/CE/ASK/AC/INV id cited in CLAUDE.md, HANDOFF.md, README.md, docs/charter.md, docs/runbooks/*, kit README exists (scripted, zero missing); runbooks and READMEs cite no repo ids
- CLAUDE.md citation meanings match their records: DEC-1, DEC-7, DEC-11, DEC-16, DEC-18, DEC-19, DEC-20, DEC-22, DEC-25, DEC-27, US-11, US-12, CE-3, CE-8, CE-10, CE-34, CE-67, AC-23 (claimed in tests/test_repo_records.py)
- FRAMEWORK §5.1/5.2/5.3/5.4/5.5/5.6/6.2/6.5/6.6/6.7/6.8/6.12/7.5/8.0/8.0.1/8.0.3/11.1 and P5/P16 exist
- banner claims that hold: NOW CE-7, NEXT CE-64; CE-7's deps all closed; ASK-5 answered by DEC-37; DEC-38's prefix list; INV-1..69 = 69 register entries; DEC-18 arbiter clause; DEC-29/31/33/34/39 meanings
- no open batons or pauses (BTN-1..3 done); all ASK-1..5 closed; orient raises none
- 'No release tag yet' true (git tag -l empty); 'Pushed through 2026-10-13e' true (origin/main == main == 8990dd0)
- framework: 0.5 (CLAUDE.md, contract.md, kit contract) matches pyproject/__version__ 0.5.0.dev0 under DEC-23
- CI gate.yml: ubuntu-latest, Python 3.12, pip install -e .[dev], pytest -q, matching CLAUDE.md § Gate
- CLI syntax cited in CLAUDE.md (record new --set/--file, ask answer --title, session close --summary 1..7) matches --help and working.py
- closed-task features exist in code: ops.py::task_close, task_reopen, decision_set, decision_relink, record_retire, decision_supersede, ask_answer, register_show, why, pause_open, banner_set, session_start; commit.py; tools/linux_gate.py
- context.toml routes: every routed path exists (G-R1 clean); evidence, spike, tools, kit, .scratch routed
- ledger/op log: newest close is 2026-10-13e, then the live 2026-10-14a session.start (the only uncommitted lines)
- criteria AC-71..80 all claimed by tests; AC-60..64 planned

## deploy-readiness

### deploy-readiness/D1 (drift, confirmed)

The top-level README tells a new user that nothing is usable, and it does not link the only install and bootstrap guide.

Evidence: README.md: "Status: pre-alpha. Nothing here is usable yet." and "exposes them through a CLI, a per-session MCP server, and a no-model housekeeping script". The housekeeping script (CE-6) is still LATER and unbuilt. README.md never links src/context_engine/kit/README.md. Yet a trial in a fresh repo of init, lint, session start, task new/promote, record new story, commit, session close and banner set worked end to end.

Fix: Update the README status line. Point it at src/context_engine/kit/README.md for install, pin and init. Mark the housekeeping script as planned (CE-6).

### deploy-readiness/D2 (drift, confirmed)

init always appends the bootloader's `## Gate` placeholder, even when CLAUDE.md already has a `## Gate` section. The result is two Gate sections, and lint stays clean.

Evidence: Trial repo3: CLAUDE.md started with `## Gate` / `pytest -q`. After init it ended with a second `## Gate` holding "`<this repo's own test command> && context-engine lint`". bootstrap.py::plan appends the whole kit/bootloader.md (`writes[CONTRACT_TARGET] = old + ...`). contract.md says the gate is "This repo's own test command, as `CLAUDE.md` § Gate names it". Already on the board as CE-51 (LATER).

Fix: Fix CE-51: when CLAUDE.md already has a `## Gate` heading, append only the kit block, without the Gate stub.

### deploy-readiness/D3 (drift, confirmed)

The 'next:' line init prints tells the user to register the MCP server, which the docs call optional. It leaves out the gate-command step and the step to commit the kit's files before session start.

Evidence: bootstrap.py::init: `nxt = "...; next: fill docs/charter.md with the owner, register the MCP server, run lint"`. The kit README § 1 and kit/contract.md say "The MCP server is optional (FRAMEWORK §11.1 ...)". Kit README § 2a steps 2-3: replace `<this repo's own test command>` in CLAUDE.md § Gate, then commit the kit's files by path before `session start`.

Fix: Change the line to: next: fill docs/charter.md with the owner, put the real test command in CLAUDE.md § Gate, run lint, commit the kit files by path (MCP server optional, kit README § 1).

### deploy-readiness/N1 (nit, confirmed)

No guard flags the `<this repo's own test command>` placeholder left in CLAUDE.md § Gate, so a repo can keep a placeholder gate with a clean lint.

Evidence: Searching src/context_engine/*.py for "own test command" finds nothing. In the trial, lint was clean with the placeholder gate.

Fix: Add a lint warning or failure, with a remedy, when the contract file still holds the bootloader's gate placeholder after the first session closes.

### deploy-readiness/N2 (nit, confirmed)

When .claude/settings.local.json already exists, init --merge-settings writes no .claude/.gitignore. It warns only in that one run's output, so the machine-specific settings file stays un-ignored and a re-run hides the warning.

Evidence: First run: skipped ".claude/.gitignore (it does not ignore settings.local.json, which holds this machine's paths: add that line...)". Second run: only ".claude/settings.local.json (holds the orient hook)". Lint is clean and settings.local.json is untracked but not ignored.

Fix: Repeat the warning on every init run while settings.local.json is not git-ignored (git check-ignore), or have lint report it.

### deploy-readiness/N3 (nit, confirmed)

`init --skip-settings` tells the user to add the hook by hand even when the hook is already there.

Evidence: In bootstrap.py::plan the `settings == "skip"` branch runs before merged_settings checks for an existing hook. On a repo that already had the hook the output was ".claude/settings.local.json (--skip-settings: add the SessionStart hook by hand, kit README § Hook)".

Fix: Check merged_settings() first. If it returns None (hook present), report '(holds the orient hook)' whatever the flag.

### deploy-readiness/N4 (nit, confirmed)

On a fresh board the first `task new` defaults to LATER and turns lint red (G-W5) without any hint. The bootstrap procedure does not say one item must be NOW.

Evidence: Trial: `task new "Try the engine"` gave "T-1: created at LATER", then lint printed "G-W5 tasks: NOW holds 0 (none); the cap is exactly 1. Remedy: re-rank with `promote`". procedures.md § Bootstrap step 4 says only "build the first board".

Fix: Have `task new` print a hint when NOW is empty, or add 'promote one item to NOW' to procedures.md § Bootstrap step 4.

### deploy-readiness/N5 (nit, confirmed)

CLI --help gives no description for most groups and options, so a new user cannot learn the formats for session close or task new from the CLI.

Evidence: Top-level `--help` gives no description for session, orient, lint, task, ask, baton, pause or banner. `session close --help` describes only --summary, nothing for --rows, --guards or --read. `task new --help` describes no option and does not list the allowed --pri values.

Fix: Add argparse help strings: --pri choices, and short format hints for --rows/--guards/--read with a pointer to manual-mode.md.

Checked and consistent:

- kit README and top-level README read as a new user; install URL github.com/averykhoo/context-engine is public (API 200) and origin/main == HEAD
- init --dry-run and init on an empty git repo: 22 files, rc 0, lint clean, routes and orient work
- init run twice: second run creates 0; CLAUDE.md and settings.local.json byte-identical
- existing CLAUDE.md content kept, kit block appended after a blank line; its @docs/framework/contract.md import resolves (file written)
- existing settings.local.json: refused with a remedy; --merge-settings keeps the permissions and adds the hook; re-run is a no-op
- SessionStart hook command (absolute paths, forward slashes) runs under bash and under cmd.exe and prints orient
- context.toml from the template parses; every route exists (G-R1 clean)
- full loop in the trial repo: session start, task new, task promote, task list, record new story --file, commit, session close, banner show, banner set --seen none; milestone commits carry the Session: trailer; the tree is clean after milestones; lint clean at the end
- fresh clone with core.autocrlf=true (CRLF files): lint clean; the engine recreates .context/.gitignore on first write
- G-D0 goes red on a contract edit and on a framework: pin change; G-R1 and G-D3 go red on a deleted runbook
- MCP server: exits 0 with stdin closed; initialize + tools/list returns 45 tools plus the instructions (ultracode wording matches DEC-30 and the contract)
- pip wheel --no-deps --no-build-isolation builds offline; the wheel holds all 14 kit files, no file missing or extra against src/context_engine, contents byte-identical
- init and lint run from the extracted wheel (context_engine.__file__ in the wheel dir): 22 files, lint clean
- stale gitignored build/lib is a subset of src, so it would not inject removed files into a wheel
- cleanup: temp dirs deleted; the only context_engine.mcp process left belongs to claude.exe, started 2026-10-13, not this audit; the repo's git status is unchanged
