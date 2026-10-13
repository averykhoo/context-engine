# Residual-risk register

Residual risks (FRAMEWORK P17, §7.4): each is a risk that was not reasonably practicable to
eliminate, with whom it affects, why it stays, the control that holds it and where it came from.
`task close` appends the residuals of a task's `## Design review`; edit an entry only when the
code changes. Ids are `INV-n`, never reused.

This is the engine's own register. It is package data, so it ships with the engine to every repo
the engine is pointed at: `context-engine register show --engine` reads it there, and `orient`
points at it (the handover, P17 regs. 7 and 11). A target repo keeps its own register for its own
risks (FRAMEWORK §10 gives its path, docs/invariants.md by default).

## INV-1: a long-lived server keeps running old engine code after the engine changes, and it may outlive `/clear`

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** Claude Code owns the server process, and the engine cannot restart itself inside a session
- **control:** individual: CLAUDE.md asks the owner to restart Claude Code after setting up or changing the server (DEC-25); CE-13 checks what `/clear` does
- **from:** CE-3, session 2026-10-12b

## INV-2: a write is logged under the wrong actor or session, because the server remembers the first `session_start` and a subagent that passes no `actor` inherits the parent's

- **affects:** every Claude Code session using the MCP tools, its subagents, the next session with no context, the owner, every repo the engine is pointed at
- **why not eliminated:** an MCP call carries no caller identity the engine can verify; the actor is self-declared (OKF §7)
- **control:** individual: the server instructions and CLAUDE.md tell each subagent to pass its own `actor`; G-W7 (CE-14) cross-checks only the session keys on board items against the op log, not who the actor was, so it does not catch this
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

## INV-14: an imported record's actor and date are read from a free-text heading, so a misread attribution is stamped as fact, and its `session` is the importing session

- **affects:** the owner, whose words in decisions must survive verbatim; the next session, which reads decisions through find, why and the index; every deployed repo (adhoc's import is CE-7); a plain-git human who edits decisions by hand
- **why not eliminated:** the single-file log has no structured fields, so only a reader can tell a misread
- **control:** collective: the whole parenthetical is kept in `attribution:` when it says more than actor and date, `imported_from:` marks every imported record, and CE-7 reviews the import diff before cutover
- **from:** CE-5, session 2026-10-12d

## INV-15: a decision's `code` links (file::symbol) rot when code moves, and why() then answers from stale links

- **affects:** the owner, whose words in decisions must survive verbatim; the next session, which reads decisions through find, why and the index; every deployed repo (adhoc's import is CE-7); a plain-git human who edits decisions by hand
- **why not eliminated:** code moves on purpose, and whether the code a link names still carries out the decision is a reading judgement no operation can make
- **control:** collective: `decision link` and `decision relink` (CE-35, AC-54) refuse a link that names no code (a file or symbol that does not exist, a blank path, a directory, a path outside the repo or written with `\`, an empty symbol part: `guards.py::code_link_problem`), so a dead link cannot be relinked to nothing; G-T3 fails a current decision's `code:` link that stops resolving, in every gate (lint, AC-47), and its remedy is `decision relink` (or `decision supersede` when the behaviour is gone); a superseded decision's links are not checked
- **from:** CE-5, session 2026-10-12d

## INV-16: G-D3 and G-T3 grep each dotted part of a symbol as a word, so a renamed symbol whose old name still appears elsewhere in the file passes

- **affects:** the building session; every later session, since lint runs in the gate (AC-23); every repo the kit deploys to, through the `[guards]` defaults; the owner, whose attention a false red costs
- **why not eliminated:** resolving definitions needs a parser per language, and the grep works for every file type
- **control:** reduce: the citing rule in CLAUDE.md (grep that a symbol exists before citing it)
- **from:** CE-14, session 2026-10-12d

## INV-17: a doc missing from a `[guards]` list is not checked at all

- **affects:** the building session; every later session, since lint runs in the gate (AC-23); every repo the kit deploys to, through the `[guards]` defaults; the owner, whose attention a false red costs
- **why not eliminated:** owner words are append-only and frozen provenance is never edited, so a red there has no remedy and the lists are chosen per repo
- **control:** collective: the kit template's default lists; the coverage guard planned in CE-30
- **from:** CE-14, session 2026-10-12d

## INV-18: G-W7 cannot recheck the values of `state`, `pri` and `deps`, only the session keys

- **affects:** the building session; every later session, since lint runs in the gate (AC-23); every repo the kit deploys to, through the `[guards]` defaults; the owner, whose attention a false red costs
- **why not eliminated:** the op log records which keys changed, not their values, and logging values would duplicate every record
- **control:** reduce: write-time refusal in `task set` (BOARD_OWNED); G-W4 and G-W5 at rest
- **from:** CE-14, session 2026-10-12d

## INV-19: G-D9's example check is a word match, so a value copied from a spec example under a note that does not say so passes

- **affects:** the building session; every later session, since lint runs in the gate (AC-23); every repo the kit deploys to, through the `[guards]` defaults; the owner, whose attention a false red costs
- **why not eliminated:** the spec's examples are prose, with no list to compare against
- **control:** individual: the `wrong if` the note must state; review of the config diff
- **from:** CE-14, session 2026-10-12d

## INV-20: G-D8 does not see a session layer written as a sentence inside a banner bullet

- **affects:** the building session; every later session, since lint runs in the gate (AC-23); every repo the kit deploys to, through the `[guards]` defaults; the owner, whose attention a false red costs
- **why not eliminated:** dated facts cite session keys mid-sentence and must pass
- **control:** reduce: G-D1 line and byte caps on the note's route (the backstop, P6)
- **from:** CE-14, session 2026-10-12d

## INV-21: a repo that copied the kit before this change keeps the old runbook and contract

- **affects:** the owner, who reads one more section at every session start; every repo the kit deploys to, whose copied runbooks and contract gain the step
- **why not eliminated:** copied runbooks go stale on upgrade by design (INV-13)
- **control:** collective: the orient heading ships in the engine, so the instruction reaches them anyway
- **from:** CE-37, session 2026-10-12e

## INV-22: a raw edit that reopens a question and also deletes `answered:` passes lint, leaving a decision whose `answers:` names an open question

- **affects:** the owner, whose answer (a stamped decision) an open question would contradict; the next session, which reads an open question as unanswered and may raise or re-answer it; a plain-git human reopening by hand from manual-mode.md; every deployed repo, which gets the engine refusal and the kit runbook copy
- **why not eliminated:** telling a deliberate repair from a mistake needs the decision's history, and no guard yet joins decisions' `answers:` to the board
- **control:** collective: manual-mode.md § task reopen and § task set say an answer changes only through its decision; the raw edit shows in the commit diff
- **from:** CE-31, session 2026-10-13a

## INV-23: an agent moves an owner's decision PROVISIONAL to BUILT, or to REJECTED or DEFERRED, without the owner having said so

- **affects:** the owner, whose decisions (owner words, stamped) carry a status, tags and attribution in frontmatter the body_sha does not cover; the next session, which reads a decision's status and the generated index as current; a plain-git human setting a decision key by hand from manual-mode.md; every deployed repo, which gets the operation and the kit runbook copy
- **why not eliminated:** whether the owner sanctioned a status move is in the owner's words, which no operation can read; the op log names session and actor and the index diff shows the move in the commit
- **control:** individual: manual-mode.md § decision set: move an owner decision's status only on the owner's words, recorded first (`record amend`)
- **from:** CE-32, session 2026-10-13a

## INV-24: an agent relinks a decision to code that resolves but does not carry the decision out (a different symbol, or a file the behaviour never moved to), so why() answers wrongly

- **affects:** the owner, whose decisions name the code that carries them out; the next session, which reads why() and `decision find --links-to` answers from `code:` links; a plain-git human relinking by hand from manual-mode.md; every deployed repo, which gets the operation and the kit runbook copy
- **why not eliminated:** whether code carries out a decision is a reading judgement no operation can make; the op log `relink` line names session and actor, and the commit diff shows old and new side by side
- **control:** individual: manual-mode.md § decision relink: relink only to where the same behaviour now lives, in the commit that moves it
- **from:** CE-35, session 2026-10-13a

## INV-25: a by-hand close (manual mode) or a raw edit still learns of the empty NOW only at the next gate run

- **affects:** the session that closes the only NOW item, which until now learned of the red G-W5 only at its next gate run; the owner, whose call the next NOW item stays; every deployed repo, whose close result line and kit runbook copy change
- **why not eliminated:** a by-hand step has no engine to warn it
- **control:** collective: manual-mode.md § task close tells the by-hand closer to count NOW after closing a NOW item and ask the owner which to promote; G-W5 reds it at rest
- **from:** CE-36, session 2026-10-13a

## INV-26: a passing mention of an id in a board item body ("G-D4 is not done here") counts as ownership

- **affects:** every later session, since lint runs in the gate (AC-23); the owner, whose attention a false red costs; every repo the kit deploys to, if the guard ships with `[guards]` defaults
- **why not eliminated:** telling ownership from mention needs judgement, and a structured owner field on every item would duplicate the map
- **control:** individual: the map's one-class-per-row rule, redone when FRAMEWORK changes materially
- **from:** CE-30, session 2026-10-13a

## INV-27: the map is FROZEN, so making the guard green after a FRAMEWORK change means a new dated map or a new board item, never an edit

- **affects:** every later session, since lint runs in the gate (AC-23); the owner, whose attention a false red costs; every repo the kit deploys to, if the guard ships with `[guards]` defaults
- **why not eliminated:** frozen provenance is never edited (CLAUDE.md)
- **control:** collective: the remedy text names both routes; filing a board item is one `task new`
- **from:** CE-30, session 2026-10-13a

## INV-28: Claude Code writes a grant into the settings file between init's re-read and its atomic replace, and that grant is lost

- **affects:** every adopting repo (CE-7's is the first) and its owner, whose CLAUDE.md init appends to and whose machine gets a local settings file; every agent session there, whose rules now load through one import and whose orient arrives by a hook; this repo's gate, through G-D0 and the kit tests
- **why not eliminated:** no lock is shared with Claude Code, so the window can be narrowed, not closed
- **control:** reduce: init re-reads the file immediately before the replace and refuses when it changed; the merge runs once, with the owner present to approve it
- **from:** CE-38, session 2026-10-13b

## INV-29: the grants (ultracode, fable, push) now sit in a framework-owned file the repo may not edit, so an owner narrows one only by a rule in CLAUDE.md that the agent must rank above the contract

- **affects:** every adopting repo (CE-7's is the first) and its owner, whose CLAUDE.md init appends to and whose machine gets a local settings file; every agent session there, whose rules now load through one import and whose orient arrives by a hook; this repo's gate, through G-D0 and the kit tests
- **why not eliminated:** the framework owning the file is the point of the bootloader (US-17)
- **control:** collective: the contract says CLAUDE.md, outside the markers, wins where it narrows or overrides a rule
- **from:** CE-38, session 2026-10-13b

## INV-30: the SessionStart hook does not run (another clone or machine, a moved interpreter, an existing local settings file init skipped), and a failing SessionStart hook is quiet by design

- **affects:** every adopting repo (CE-7's is the first) and its owner, whose CLAUDE.md init appends to and whose machine gets a local settings file; every agent session there, whose rules now load through one import and whose orient arrives by a hook; this repo's gate, through G-D0 and the kit tests
- **why not eliminated:** Claude Code documents that a SessionStart hook cannot block, and the local settings file is machine-specific and gitignored, so lint cannot see it
- **control:** individual: the contract's session-start rule: if no orient output is in context, run session start and orient by hand and tell the owner the hook did not run
- **from:** CE-38, session 2026-10-13b

## INV-31: Claude Code's behaviour on a missing @-import target, whether hook output reaches context on resume and after /clear, and which shell runs a hook on Windows (the command runs under bash and cmd.exe, not PowerShell) are documented only in part and not probed on a live session

- **affects:** every adopting repo (CE-7's is the first) and its owner, whose CLAUDE.md init appends to and whose machine gets a local settings file; every agent session there, whose rules now load through one import and whose orient arrives by a hook; this repo's gate, through G-D0 and the kit tests
- **why not eliminated:** a probe needs an interactive Claude Code session, which an agent cannot launch
- **control:** individual: G-D0 and orient make a missing target loud regardless; the owner runs the probes (task log, CE-38 close)
- **from:** CE-38, session 2026-10-13b

## INV-32: G-D0 reds an adopted repo after an engine reinstall whose kit contract changed within the same major.minor

- **affects:** every adopting repo (CE-7's is the first) and its owner, whose CLAUDE.md init appends to and whose machine gets a local settings file; every agent session there, whose rules now load through one import and whose orient arrives by a hook; this repo's gate, through G-D0 and the kit tests
- **why not eliminated:** equality with the installed kit is what makes "the framework owns the file" mechanical
- **control:** collective: the red's remedy is one copy, the same step as the upgrade ritual (kit README § Upgrade)
- **from:** CE-38, session 2026-10-13b
