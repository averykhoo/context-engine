# Residual-risk register

LIVING. Residual risks (FRAMEWORK P17, §7.4): each is a risk that was not reasonably practicable to
eliminate, with whom it affects, why it stays, the control that holds it and where it came from.
`task close` appends the residual risks of a task's `## Design review`; edit an entry only when the
code changes. Ids are `INV-n`, never reused.

This is the engine's own register. It is package data, so it ships with the engine to every repo
the engine is pointed at: `context-engine register show --engine` reads it there, and `orient`
points at it, so it reaches every repo that adopts the engine (P17: regulations 7 and 11 of
Singapore's Design for Safety Regulations). A target repo keeps its own register for its own
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

- **affects:** a session running a procedure by hand (no engine, or an engine that errs), the session adopting a repo, the adopting repo's owner and its plain-git humans, the next session with no context, every repo the engine is pointed at
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
- **control:** collective: the red's remedy is one copy, the same step as the upgrade procedure (kit README § Upgrade)
- **from:** CE-38, session 2026-10-13b

## INV-33: a test that carries the marker but does not check its criterion (a skipped test, an assert that cannot fail) satisfies G-T2

- **affects:** every later session, since lint runs in the gate (AC-23) and a false red stops all work; the owner, whose charter and stories the guards read and who answers the open questions below; every repo the kit deploys to, since G-I2, G-T1 and G-T2 are in the §11.1 minimum set and ship with `[guards]` defaults; a plain-git human who edits `docs/criteria.md` or a test by hand
- **why not eliminated:** the guard sees annotations, not coverage (FRAMEWORK §3.4); proving a test checks its claim is mutation, which is CE-34
- **control:** individual: the sabotage rule (DEC-11), under which a criterion moves to tested only after its claiming test was seen red; G-T5 (CE-34) mechanises it later
- **from:** CE-25, session 2026-10-13b

## INV-34: G-T1's `unspecified` with a board task is satisfied by any board file that mentions the story id, a passing mention included

- **affects:** every later session, since lint runs in the gate (AC-23) and a false red stops all work; the owner, whose charter and stories the guards read and who answers the open questions below; every repo the kit deploys to, since G-I2, G-T1 and G-T2 are in the §11.1 minimum set and ship with `[guards]` defaults; a plain-git human who edits `docs/criteria.md` or a test by hand
- **why not eliminated:** telling a task that specifies the story from one that mentions it needs judgement, as with G-D12
- **control:** individual: the session reads the named item at intake; the guard's message names the item it counted
- **from:** CE-25, session 2026-10-13b

## INV-35: intake steps 5 (contradiction check) and 6 (criteria census) get no tool, so a session can skip them

- **affects:** every later session, since lint runs in the gate (AC-23) and a false red stops all work; the owner, whose charter and stories the guards read and who answers the open questions below; every repo the kit deploys to, since G-I2, G-T1 and G-T2 are in the §11.1 minimum set and ship with `[guards]` defaults; a plain-git human who edits `docs/criteria.md` or a test by hand
- **why not eliminated:** finding a contradiction or classing a criterion KEEP, rewrite or retire is judgement no lint can make (P8)
- **control:** individual: procedures.md § Intake steps 5 and 6 and the census evidence doc; the next coverage map marks them deliberately prose-only, so G7 counts them
- **from:** CE-25, session 2026-10-13b

## INV-36: an upgraded repo can lack the method runbooks with lint clean, since init never edits an existing context.toml and the new routes are added by hand while the contract names those files

- **affects:** every repo the kit deploys to, since init copies the four method runbooks and the template routes them; every later session here, which reads gate.md, sabotage.md, fan-out.md and release.md as method; the owner, whose global CLAUDE.md rules (CI watcher, install trial, delegation) the runbooks distil
- **why not eliminated:** init does not rewrite an owner's config (DEC-1, DEC-32)
- **control:** collective: G-D0 (CE-50) fails, in a repo with this engine's kit block, each runbook the installed kit ships that is missing from the repo or that no route covers; individual: kit README § 4 upgrade step, which merges a runbook the repo edited
- **from:** CE-26, session 2026-10-13c

## INV-37: a repo's own file under a method runbook's name takes the framework runbook's place (init skips it, it gains the route's caps and the contract's pointer)

- **affects:** every repo the kit deploys to, since init copies the four method runbooks and the template routes them; every later session here, which reads gate.md, sabotage.md, fan-out.md and release.md as method; the owner, whose global CLAUDE.md rules (CI watcher, install trial, delegation) the runbooks distil
- **why not eliminated:** init never overwrites
- **control:** individual: kit README § 3 and init's skipped output
- **from:** CE-26, session 2026-10-13c

## INV-38: adopted runbook copies drift from the kit after init and nothing compares them

- **affects:** every repo the kit deploys to, since init copies the four method runbooks and the template routes them; every later session here, which reads gate.md, sabotage.md, fan-out.md and release.md as method; the owner, whose global CLAUDE.md rules (CI watcher, install trial, delegation) the runbooks distil
- **why not eliminated:** they are the repo's own once copied
- **control:** individual: kit README § 4 upgrade step (continues CE-24's residual)
- **from:** CE-26, session 2026-10-13c

## INV-39: a runbook's method can be wrong while every check passes, since the tests check shape (set, routes, liveness, step names, leaks), not the method

- **affects:** every repo the kit deploys to, since init copies the four method runbooks and the template routes them; every later session here, which reads gate.md, sabotage.md, fan-out.md and release.md as method; the owner, whose global CLAUDE.md rules (CI watcher, install trial, delegation) the runbooks distil
- **why not eliminated:** judging a method is review, not lint (P8)
- **control:** individual: design review and the three-lens review at build
- **from:** CE-26, session 2026-10-13c

## INV-40: the leak check is a deny-list, so a new repo-specific id prefix or path form passes until someone adds it

- **affects:** every repo the kit deploys to, since init copies the four method runbooks and the template routes them; every later session here, which reads gate.md, sabotage.md, fan-out.md and release.md as method; the owner, whose global CLAUDE.md rules (CI watcher, install trial, delegation) the runbooks distil
- **why not eliminated:** an allow-list of framework id forms is not built
- **control:** individual: tests/test_kit.py::LEAK, extended when a leak is found
- **from:** CE-26, session 2026-10-13c

## INV-41: a hook slower than lock_timeout (30s) makes other sessions' writes refuse while it runs

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** a commit hook's time is the repo's, not the engine's
- **control:** individual: they refuse before writing; the git call times out at 120s
- **from:** CE-45, session 2026-10-13c

## INV-42: another session's hand edit in progress to a file an op names (HANDOFF.md via banner set, a task body) is committed as it stands

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** telling an op's change from a hand edit in the same file is not cheap; the engine already rewrote the whole file before
- **control:** individual: the op's line names the sessions whose lines it carried
- **from:** CE-45, session 2026-10-13c

## INV-43: an error other than a Refusal partway through a multi-write op commits a half-made change silently

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** the commit runs on the lock's exit whatever ended the op
- **control:** individual: lint reports the half-made state
- **from:** CE-45, session 2026-10-13c

## INV-44: G-W7 cannot see an op line whose record is missing at HEAD, which a by-hand commit can make

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** no guard checks op lines against paths at rest
- **control:** individual: the engine never makes such a commit; manual-mode § Commit the write
- **from:** CE-45, session 2026-10-13c

## INV-45: a pause's uncommitted list is read before its own commit, so it can list paths that commit then sweeps in

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** the list is reported before the commit runs
- **control:** individual: the op's line names the commit's sha
- **from:** CE-45, session 2026-10-13c

## INV-46: merge=union can reorder or duplicate op lines from two branches, and G-W7 takes newest from file order

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** union merge does not order lines
- **control:** individual: lint after a merge; procedures § Reconciling foreign commits
- **from:** CE-45, session 2026-10-13c

## INV-47: every write is a commit, so history grows fast and each write costs about 0.5s under the lock on Windows

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** FRAMEWORK §5.5 rule 4 chooses a commit per write over a dirty tree
- **control:** individual: [engine] commit = false turns it off (a pause still commits)
- **from:** CE-45, session 2026-10-13c

## INV-48: an older engine refuses a context.toml carrying [engine] commit

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** kit version skew between repos
- **control:** individual: kit README upgrade step
- **from:** CE-45, session 2026-10-13c

## INV-49: under git's reftable format HEAD falls back to symbolic-ref, a path no test covers

- **affects:** every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- **why not eliminated:** no reftable repo in the test matrix
- **control:** individual: none beyond the detached-HEAD skip
- **from:** CE-45, session 2026-10-13c

## INV-50: a hand-forged retire line in the op log, or a deleted retire amendment, passes G-I2

- **affects:** the owner, whose stories are retired and whose words record why; every agent session, which follows the G-I1 and G-I2 remedies and intake step 5; every repo the kit deploys to, whose stories retired by hand before adoption now go G-I2 red
- **why not eliminated:** the op log and amendments are trusted as written, as G-W7 trusts them
- **control:** individual: FRAMEWORK §8.1 G-I2 names it under Not checked; review at intake
- **from:** CE-49, session 2026-10-13c

## INV-51: a hand edit between live, unspecified and unconfirmed passes lint

- **affects:** the owner, whose confirmations are recorded; every repo the kit deploys to, where a reconstruction confirmed by hand before adoption goes G-I2 red until record confirm records the owner's words
- **why not eliminated:** no operation owns the move between live and unspecified, and the op log records keys, not values; an actor rewritten by hand (a reconstruction turned into owner) gets past the confirm check
- **control:** individual: G-I2 (guards.py::confirm_problems) fails a reconstruction that is live or unspecified with no logged record confirm, and a confirmed story made unconfirmed again (CE-58)
- **from:** CE-49, session 2026-10-13c

## INV-52: supersedes and superseded_by not mirrored, a self link or a cycle passes, for stories and decisions both

- **affects:** the owner, whose stories are retired and whose words record why; every agent session, which follows the G-I1 and G-I2 remedies and intake step 5; every repo the kit deploys to, whose stories retired by hand before adoption now go G-I2 red
- **why not eliminated:** no mirror guard exists
- **control:** individual: record retire writes both directions; a mirror guard is the follow-up
- **from:** CE-49, session 2026-10-13c

## INV-53: G-D5 misses counts outside its census form (another adjective, as in "four method runbooks"; `**23**`; spelled numbers above twenty; singulars; a count split across lines)

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** the measurement showed wider patterns are noise (27 hits, 25 not counts)
- **control:** individual: the numbers docstring's Not checked list; review
- **from:** CE-33, session 2026-10-13c

## INV-54: G-D5 is red on a label or a rule value without a bound word (`Step 3 checks`, `the last 5 entries`)

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** telling a label from a count needs judgement, and a wider bound escape is a false-pass hole
- **control:** individual: the remedy names backticks
- **from:** CE-33, session 2026-10-13c

## INV-55: a YYYY-MM-DD anywhere on a line (a link target too) exempts every count on it

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** P5's form is a key on the line, and a narrower rule cannot be followed by hand
- **control:** individual: review
- **from:** CE-33, session 2026-10-13c

## INV-56: G-D5 trusts a FROZEN or ACTIVE-PLAN word G-D4 does not check when a numbers doc is not under liveness

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** both lists are config
- **control:** individual: §8.3 says to list each numbers doc under liveness too, and this repo does
- **from:** CE-33, session 2026-10-13c

## INV-57: a liveness_given glob wide enough to cover every listed doc passes them all

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** reviewed config; only a stale glob is checked
- **control:** individual: review of context.toml changes
- **from:** CE-33, session 2026-10-13c

## INV-58: a declaration may be false (a LIVING doc gone stale)

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** no mechanical check (DR9)
- **control:** individual: housekeeping and review
- **from:** CE-33, session 2026-10-13c

## INV-59: an adopting repo is red after init until its own docs declare liveness

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** P2 asks every doc to declare, so hiding them would be a false green
- **control:** individual: kit README §3, the remedy text
- **from:** CE-33, session 2026-10-13c

## INV-60: banner set and other writes can store text G-D5 reds, and the engine commits it

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** reduced, not eliminated, by CE-63 (session 2026-10-22b): `banner set`, `session close` and `session pause` refuse text that adds a G-D1, G-D5 or G-D8 failure, by calling lint's own functions before writing, and `context-engine commit` refuses a path lint fails. What stays: a hand edit (no write to check); the engine's other writes (a task body or comment, `doc freeze`, a baton or pause record, the session-start stub), which are not checked and may commit at a milestone, which runs no lint; and a write that makes an existing failure worse without adding one (a second wide line, a longer over-cap note)
- **control:** reduce at source: the write-time refusal (guards.py::prose_failures, via working.py::Engine._refuse_prose) and the commit's lint (working.py::Engine._lint_carried); collective: lint in the gate before the next commit
- **from:** CE-33, session 2026-10-13c

## INV-61: the shared prose() reads a leading `---` break as frontmatter and lets `~~~` close a ``` fence, hiding lines from G-D5 (and G-D3, G-D7)

- **affects:** every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- **why not eliminated:** pre-existing in the shared reader
- **control:** individual: none yet; a follow-up
- **from:** CE-33, session 2026-10-13c

## INV-62: a plain `git commit -o` naming a record whose op line rides along commits the record without its line, and G-W7 reds that commit on a clean checkout

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** a session or a human can always run git directly
- **control:** collective: the contract and procedures name `context-engine commit`; CI lints the pushed tip; the next milestone carries the line
- **from:** CE-55, session 2026-10-13c

## INV-63: between milestones, board writes live only in the shared working tree, where a `git stash`, reset or checkout of those paths by anyone loses them

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** DEC-36 trades per-write commits for a shorter history; what rides along is cheap to redo
- **control:** individual: the contract forbids stash; owner words, hand-offs and closes commit at once
- **from:** CE-55, session 2026-10-13c

## INV-64: another session's half-done hand edit that still parses is committed as it stands by any session's milestone

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** telling an op's change from a hand edit in the same file is not cheap
- **control:** individual: the line names the sessions whose lines it carried; lint at the next gate
- **from:** CE-55, session 2026-10-13c

## INV-65: `context-engine commit` runs no gate, so a session can commit red code through it

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** git commit runs none either, and a gate inside would hold the lock for minutes
- **control:** individual: contract § Gate and manual-mode § context-engine commit say to run the gate first; CI on every push
- **from:** CE-55, session 2026-10-13c

## INV-66: an upgraded repo saying `commit = true` moves from every write to milestones with no line saying so

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** CE-45's template wrote `true` as the default, and DEC-36 changes the default
- **control:** individual: kit README § Upgrade says so and names `"every-write"` to keep the old behaviour
- **from:** CE-55, session 2026-10-13c

## INV-67: an older engine refuses the template's `commit = "milestones"`

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** kit version skew between machines
- **control:** individual: kit README bootstrap and upgrade notes say to write `true` until every machine runs this engine
- **from:** CE-55, session 2026-10-13c

## INV-68: every adopting repo's G-D0 is red until it copies the changed kit contract

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** the contract's text changed without a framework version change
- **control:** individual: G-D0 names the fix; kit README § Upgrade step 2
- **from:** CE-55, session 2026-10-13c

## INV-69: the foreign-reconcile baseline (the newest ledger commit this session did not make) can skip a foreign commit made while another session was open, and any milestone now touches the ledger

- **affects:** every session in every repo the engine runs in, whose board writes now stay in the working tree until the next milestone; other sessions sharing a working tree, whose riding writes and hand edits any session's milestone sweeps; the owner, whose history gains a commit per milestone instead of per write, and whose task closes now commit with Closes:; adopting repos, whose `commit = true` now means milestones and whose G-D0 is red until they copy the changed contract; a plain-git human who commits records by hand
- **why not eliminated:** the baseline predates CE-55, which widens it
- **control:** individual: procedures § Reconciling foreign commits only; follow-up filed
- **from:** CE-55, session 2026-10-13c

## INV-70: a setext `Gate` heading is not detected, so such a repo still gets a second Gate

- **affects:** every repo adopting the engine whose CLAUDE.md already has a gate; the owner reading CLAUDE.md after init; the first session there, which runs the gate CLAUDE.md names
- **why not eliminated:** setext headings in CLAUDE.md are rare and parsing them needs a markdown parser
- **control:** individual: init's output names the CLAUDE.md change, and the kit README and manual-mode say which headings count
- **from:** CE-51, session 2026-10-14a

## INV-71: a repo whose real gate is a `### Gate` gets the stub appended beside it

- **affects:** every repo adopting the engine whose CLAUDE.md already has a gate; the owner reading CLAUDE.md after init; the first session there, which runs the gate CLAUDE.md names
- **why not eliminated:** a level-3 Gate is usually a subsection, not the repo's gate
- **control:** individual: init's label quotes the heading it took; the kit README and manual-mode say which headings count
- **from:** CE-51, session 2026-10-14a

## INV-72: _ignored does not read .git/info/exclude, the global excludes file or nested ignore files

- **affects:** the owner and first session in every adopting repo, who follow init's next: line and hints; a person using plain git, whose .claude/settings.local.json may be committed
- **why not eliminated:** reproducing git's full ignore resolution is not cheap, and erring toward a warning is safe
- **control:** individual: init warns or writes the ignore file; `git check-ignore` is the by-hand check (manual-mode § init)
- **from:** CE-70, session 2026-10-14a

## INV-73: ask answer wraps the words in `*"..."*`, so multi-paragraph words from --file render with stray asterisks

- **affects:** the owner, whose words must land verbatim; the session doing intake, which must not pass words through a heredoc
- **why not eliminated:** a blockquote would render well but the stored text would no longer be byte-verbatim
- **control:** individual: the words are stored verbatim; the rendering is cosmetic
- **from:** CE-73, session 2026-10-14a

## INV-74: this repo's routine orient cuts its own banner, against orient_max_bytes's provenance

- **affects:** every session in every repo, which starts from orient; the owner, who must see batons, pauses, other sessions and questions; a cold session in a repo with a large banner
- **why not eliminated:** the banner is the session's to write
- **control:** individual: banner set says when orient will cut the new banner (CE-76); the cut note points at banner show
- **from:** CE-75, session 2026-10-14a

## INV-75: orient displays batons before other open sessions, while the contract and procedures order other sessions first

- **affects:** every session in every repo, which starts from orient; the owner, who must see batons, pauses, other sessions and questions; a cold session in a repo with a large banner
- **why not eliminated:** display order is cosmetic and swapping it renumbers shared runbook items
- **control:** individual: the procedure's order governs what the session does
- **from:** CE-75, session 2026-10-14a

## INV-76: an orient_max_bytes below about 250 bytes cannot hold the headings

- **affects:** every session in every repo, which starts from orient; the owner, who must see batons, pauses, other sessions and questions; a cold session in a repo with a large banner
- **why not eliminated:** no repo sets it that low
- **control:** individual: manual-mode § orient documents the floor
- **from:** CE-75, session 2026-10-14a

## INV-77: the questions cut note lists every open question, not which are pending, and no note says N of M shown

- **affects:** every session in every repo, which starts from orient; the owner, who must see batons, pauses, other sessions and questions; a cold session in a repo with a large banner
- **why not eliminated:** a precise per-section count needs another read op
- **control:** individual: task list shows each question's state
- **from:** CE-75, session 2026-10-14a

## INV-78: answered questions from the old log (adhoc Q1..Q8) have no alias that resolves

- **affects:** every repo adopting the engine with an existing id series (adhoc first); the owner, whose old ids are cited in commits, code and prose; every session that resolves an id; a person reading plain files
- **why not eliminated:** a decision's aliases are fixed and ask answer cannot close on an existing decision
- **control:** individual: kit README § 3 says answered questions stay history
- **from:** CE-74, session 2026-10-14a

## INV-79: ids cited in imported bodies and titles stay plain text, so why misses them until linked by hand

- **affects:** every repo adopting the engine with an existing id series (adhoc first); the owner, whose old ids are cited in commits, code and prose; every session that resolves an id; a person reading plain files
- **why not eliminated:** parsing prose citations into links is not cheap or reliable
- **control:** individual: decision link by hand; manual-mode § decision import
- **from:** CE-74, session 2026-10-14a

## INV-80: a rejected row's new number (DEC-45..) can be read by a human as the old D-45 written later

- **affects:** every repo adopting the engine with an existing id series (adhoc first); the owner, whose old ids are cited in commits, code and prose; every session that resolves an id; a person reading plain files
- **why not eliminated:** rejected rows have no old number to keep
- **control:** collective: procedures § Bootstrap and kit README § 3 say to freeze the old log until the merge; the CE-7 trap re-checks it
- **from:** CE-74, session 2026-10-14a

## INV-81: task aliases can be moved or unset, so an old id can come to name a different record

- **affects:** every repo adopting the engine with an existing id series (adhoc first); the owner, whose old ids are cited in commits, code and prose; every session that resolves an id; a person reading plain files
- **why not eliminated:** boards are rewritten as work moves
- **control:** individual: task set names every alias it drops
- **from:** CE-74, session 2026-10-14a

## INV-82: a kind added later whose prefix matches existing aliases turns G-D2 red with no runbook fix

- **affects:** every repo adopting the engine with an existing id series (adhoc first); the owner, whose old ids are cited in commits, code and prose; every session that resolves an id; a person reading plain files
- **why not eliminated:** aliases on append-only decisions are fixed
- **control:** individual: G-D2 names the clash
- **from:** CE-74, session 2026-10-14a

## INV-83: dep, close, promote and comment take only live ids

- **affects:** every repo adopting the engine with an existing id series (adhoc first); the owner, whose old ids are cited in commits, code and prose; every session that resolves an id; a person reading plain files
- **why not eliminated:** writes resolve aliases only where a lookup is read
- **control:** individual: the refusal points at task show
- **from:** CE-74, session 2026-10-14a

## INV-84: a ruling made on the owner's delegation but recorded with neither `ruled_by` nor a `## Ruling` section reads as the owner's own decision, so neither G-I3 nor the write-time refusals of `record new` and `ask answer` can see it

- **affects:** the owner, whose delegated call would read as their own frozen words; every later session that reads that decision as owner intent
- **why not eliminated:** the file then looks exactly like an owner decision; only the transcript shows that the owner delegated the call, and the engine never reads the transcript
- **control:** individual: the contract's "Who decides" rule and FRAMEWORK §6.5 (a delegated call is recorded with `ruled_by`, never as `actor: owner`); G-I3 for every decision that names `ruled_by` or holds a `## Ruling` section
- **from:** CE-139, session 2026-10-30a

## INV-85: an open item's kill bar can be emptied or rewritten after its run, so the item closes without a verdict or against the new bar

- **affects:** owners and reviewers trusting a recorded verdict
- **why not eliminated:** the engine cannot tell a correction before the run from a change after it
- **control:** individual: the op log's section lines; the reviewer reads them (FRAMEWORK §5.2, manual-mode § task close)
- **from:** CE-108, session 2026-10-30a

## INV-86: a guards receipt passes gate_receipt on the words 'not run' anywhere in it (e.g. 'lint not run'), with no gate result

- **affects:** owners reading a close's guards receipt as proof the gate ran
- **why not eliminated:** the check is a presence check by design; it cannot tell whether the statement is true or about the gate
- **control:** individual: the receipt is verbatim in the ledger and the close digest, read by the owner; docstring Not checked
- **from:** CE-123, session 2026-10-30a
