# Residual-risk register

Residual risks (FRAMEWORK P17, §7.4): each is a risk that was not reasonably practicable to
eliminate, with whom it affects, why it stays, the control that holds it and where it came from.
`task close` appends the residuals of a task's `## Design review`; edit an entry only when the
code changes. Ids are `INV-n`, never reused.

This is the engine's own register. It is package data, so it ships with the engine to every repo
the engine is pointed at: `context-engine register show --engine` reads it there, and `orient`
points at it (the handover, P17 regs. 7 and 11). A target repo keeps its own register for its own
risks (FRAMEWORK §10: `docs/invariants.md`).

## INV-1: a long-lived server keeps running old engine code after the engine changes, and it may outlive `/clear`

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** Claude Code owns the server process, and the engine cannot restart itself inside a session
- **control:** individual: CLAUDE.md asks the owner to restart Claude Code after setting up or changing the server (DEC-25); CE-13 checks what `/clear` does
- **from:** CE-3, session 2026-10-12b

## INV-2: a write is logged under the wrong actor or session, because the server remembers the first `session_start` and a subagent that passes no `actor` inherits the parent's

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** an MCP call carries no caller identity the engine can verify; the actor is self-declared (OKF §7)
- **control:** individual: the server instructions and CLAUDE.md tell each subagent to pass its own `actor`; G-W7 (not built, CE-14) will cross-check the op log
- **from:** CE-3, session 2026-10-12b

## INV-3: the MCP tools are missing at session start, and a session works around them silently

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** whether the server is registered lives in the user's Claude Code config, outside the repo
- **control:** individual: CLAUDE.md's rule (DEC-25): set the server up, use the CLI for the session, ask the owner to restart; manual-mode.md § When the MCP tools are missing
- **from:** CE-3, session 2026-10-12b

## INV-4: a task that should carry `review` is left without it, so it gets no ceremony

- **affects:** the session building or closing a reviewed task, the next session with no context, the owner, a human editing tasks with plain git, every repo the engine is pointed at
- **why not eliminated:** the threshold is declared by the task's author; detecting the triggers from a diff is out of scope and would misfire on small edits
- **control:** individual: FRAMEWORK §5.2's threshold list and the runbook's `task set` note
- **from:** CE-23, session 2026-10-12b

## INV-5: a close refused after its register append leaves INV entries for a task that is still open

- **affects:** the session building or closing a reviewed task, the next session with no context, the owner, a human editing tasks with plain git, every repo the engine is pointed at
- **why not eliminated:** the store's lock is not re-entrant and the register is not a record, so the two writes cannot be one atomic write
- **control:** reduce: the append runs inside the close's check(), after the review is validated, and is idempotent, so the next close reuses the entries
- **from:** CE-23, session 2026-10-12b

## INV-6: a repo runs an older installed engine, so the register it is handed is stale

- **affects:** the session building or closing a reviewed task, the next session with no context, the owner, a human editing tasks with plain git, every repo the engine is pointed at
- **why not eliminated:** the handover is only as fresh as the installed engine (DEC-1: the engine is pointed at a repo, never vendored into it)
- **control:** individual: orient prints the engine version beside the count; reinstall the engine
- **from:** CE-23, session 2026-10-12b

## INV-7: an adopted repo runs an engine whose major.minor no longer matches its committed `framework:` line or kit block

- **affects:** the session adopting a repo, the adopting repo's owner and its plain-git humans, the repo's own environment and files, the next session in that repo with no context, every repo the engine is pointed at
- **why not eliminated:** the engine is installed outside the repo (DEC-1), so a repo cannot stop its owner running another engine; and the kit marker version in bootstrap.BEGIN is still a literal not tied to __version__
- **control:** collective: G-D0 (CE-21, working.py::Engine.lint_contract) turns lint red when the contract's `framework:` line or kit-block marker names another major.minor than the installed engine, naming the upgrade remedy; an engine version bump that leaves bootstrap.BEGIN behind fails the engine's own gate, because test_kit.py::test_an_empty_repo_bootstraps_with_init_alone_and_runs_a_whole_session lints a fresh init; individual: the kit README § 4 (Upgrade) steps and the pin in the first ledger summary
- **from:** CE-15, session 2026-10-12b

## INV-8: adopters pin the engine by a bare commit SHA, because there is no release tag

- **affects:** the session adopting a repo, the adopting repo's owner and its plain-git humans, the repo's own environment and files, the next session in that repo with no context, every repo the engine is pointed at
- **why not eliminated:** cutting a release tag is the owner's call
- **control:** individual: the kit README § 1 (Install and pin) says to pin a full commit SHA until releases exist and to record the ref in the first ledger summary
- **from:** CE-15, session 2026-10-12b

## INV-9: the runbooks are not in the kit, and manual-mode.md still carries this repo's ids, so an adopter without the engine has no by-hand fallback on disk

- **affects:** the session adopting a repo, the adopting repo's owner and its plain-git humans, the repo's own environment and files, the next session in that repo with no context, every repo the engine is pointed at
- **why not eliminated:** de-leaking the runbooks so they can ship is CE-24's scope (CE-7 depends on it)
- **control:** collective: since CE-24 the kit ships both runbooks and `init` copies them (test_init_copies_the_runbooks_and_keeps_an_edited_one), and test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths keeps them free of this repo's ids
- **from:** CE-15, session 2026-10-12b

## INV-10: the kit's default prefixes collide with ids the adopting repo already uses outside the engine's record directories

- **affects:** the session adopting a repo, the adopting repo's owner and its plain-git humans, the repo's own environment and files, the next session in that repo with no context, every repo the engine is pointed at
- **why not eliminated:** the engine cannot see ids in files it is not pointed at
- **control:** individual: init's --prefix override and the context.toml.template comments on mapping an existing repo (FRAMEWORK §11.4, map rather than move)
- **from:** CE-15, session 2026-10-12b

## INV-11: a kit file added in a new subdirectory is not shipped in the wheel

- **affects:** the session adopting a repo, the adopting repo's owner and its plain-git humans, the repo's own environment and files, the next session in that repo with no context, every repo the engine is pointed at
- **why not eliminated:** what ships is whatever pyproject's package-data globs match, and a packaging change can still narrow them
- **control:** collective: since CE-24 the glob is `kit/**/*`, and test_the_wheel_carries_every_kit_file builds a wheel in the gate and checks every kit file is in it
- **from:** CE-15, session 2026-10-12b

## INV-12: an edit to CLAUDE.md that lands between init's re-read and its rewrite is lost

- **affects:** the session adopting a repo, the adopting repo's owner and its plain-git humans, the repo's own environment and files, the next session in that repo with no context, every repo the engine is pointed at
- **why not eliminated:** init runs before the repo has a context.toml naming a lock file, so it takes no lock, and a plain file has no compare-and-swap; the window is one re-read to one write
- **control:** reduce: bootstrap._write's re-check narrows it to that window; `init --dry-run` first; git shows a lost edit to a tracked CLAUDE.md
- **from:** CE-15, session 2026-10-12b

## INV-13: an adopter's copied runbooks go stale against a newer engine, because init never overwrites them

- **affects:** a session running a ritual by hand (no engine, or an engine that errs), the session adopting a repo, the adopting repo's owner and its plain-git humans, the next session with no context, every repo the engine is pointed at
- **why not eliminated:** the copy in the repo is the adopter's own and may carry its edits, so neither init nor an upgrade may replace it unasked
- **control:** individual: the kit README § Upgrade step to replace each kit runbook the repo has not edited; G-D0 flags a major.minor change
- **from:** CE-24, session 2026-10-12d
