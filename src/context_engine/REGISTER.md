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
- **control:** individual: G-D0 and orient make a missing target loud regardless; the owner runs the probes (task log, CE-38 close). After a compaction (G-6; folded in from CE-145 by DEC-132): the hook half was seen in adhoc on 2026-10-26a (CE-79 log); the agent half waits for a natural compaction in adhoc, not a forced one. It counts as seen when the agent's first turn after that compaction keeps its old session key and adhoc's ledger shows no second `session start`; whoever sees it writes a new dated evidence doc, `docs/evidence/inv31-compaction-<date>.md` (FROZEN, citing the 2026-10-23 probe), with transcript, line and key (DEC-133)
- **from:** CE-38, session 2026-10-13b; amended by CE-145 (DEC-132), session 2026-10-31a

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

## INV-86: a guards receipt passes gate_receipt on a 'not run' that opens it or is said of the gate in the same clause, true or not, with no gate result

- **affects:** owners reading a close's guards receipt as proof the gate ran
- **why not eliminated:** the check is a presence check by design; it cannot tell whether the statement is true
- **control:** technical: the default pattern counts `not run` only opening the receipt or said of the gate (`^\s*not run\b|\bgate\b[^;,.]*?\bnot run\b`), so "lint not run" is refused (CE-165, DEC-288); individual: the receipt is verbatim in the ledger and the close digest, read by the owner; docstring Not checked
- **from:** CE-123, session 2026-10-30a; narrowed by CE-165, session 2026-11-07e

## INV-87: neither the criterion ops nor lint check that a retired criteria row names the decision that retired it, that a deviates row names its deviation entry, or that a story marked sign-off: required keeps its criteria planned (FRAMEWORK §3.3)

- **affects:** owners who rely on sign-off: required
- **why not eliminated:** no guard reads these yet, and the shape of sign-off/verified is not settled (FRAMEWORK §9.3)
- **control:** individual: intake by hand, plus Not checked in working.py::Engine.criterion_new's docstring and manual-mode § criterion set
- **from:** CE-42, session 2026-10-30a

## INV-88: a settings orient hook whose matcher is narrower than every source (for example startup only) still makes the plugin stay quiet, so orient does not run on resume, clear or compact; the launcher's scanner reads every command key, not only SessionStart ones

- **affects:** repos running the plugin beside a hand-written settings orient hook
- **why not eliminated:** judging matchers needs a JSON parser in the POSIX launcher, which has none (DEC-124)
- **control:** individual: kit README § Hook tells the owner to keep one SessionStart orient hook for every source
- **from:** CE-146, session 2026-10-30a

## INV-89: the plugin launcher judges a settings orient hook by its text and never runs or expands it, so beside a hook that would fail (an engine present but broken), or whose program or --root names a variable or ~ that expands to a stale path or that its shell never expands, it stays quiet and orient fails silently

- **affects:** repos running the plugin beside a settings orient hook, among them those whose committed hook uses $CLAUDE_PROJECT_DIR, %VAR% or ~
- **why not eliminated:** running the hook to find out would run orient twice (DEC-124 option d), and the hook's shell expands a variable or ~ where the launcher cannot (DEC-124)
- **control:** individual: contract § Session start: a failing hook is silent, so the agent says so when orient is missing from its context
- **from:** CE-146, session 2026-10-30a
- **merged:** INV-90 folded into this entry, session 2026-11-06c (DEC-162)

## INV-90: (retired 2026-11-06c: merged into INV-89, DEC-162) the plugin launcher trusts a settings orient hook whose program or --root names a variable or starts with ~ without checking it, so one that expands to a stale path, or that quotes ~ or single-quotes a variable so its shell never expands it, keeps the plugin quiet

- **affects:** repos whose committed settings hook uses $CLAUDE_PROJECT_DIR, %VAR% or ~
- **why not eliminated:** the hook's shell expands it and the launcher cannot (DEC-124)
- **control:** individual: contract § Session start: a failing hook is silent, so the agent says so when orient is missing from its context
- **from:** CE-146, session 2026-10-30a
- **retired:** session 2026-11-06c (claude-code/claude-opus-5-5): merged into INV-89 (DEC-162); kept so its id is never reused

## INV-91: In an adopting repo's shallow CI checkout, G-W9 trusts history it cannot see and G-W11 skips

- **affects:** adopting repos whose CI clones shallow
- **why not eliminated:** a depth-1 clone lacks the cited commits, and a guard cannot fetch them
- **control:** reduce: this repo's CI fetches full history (fetch-depth: 0, test_ci.py); docs/runbooks/gate.md says so for adopters
- **from:** CE-6, session 2026-11-01b

## INV-92: G-W11 can turn another session's gate red while a live but idle session has not run session touch; its window of 3 is unmeasured

- **affects:** repos running concurrent sessions
- **why not eliminated:** DEC-138 un-deferred it without a measurement, since CE-7 closed without one
- **control:** individual: the remedy tells the agent to ask the owner before abandoning; session touch resets it (DEC-29, DEC-138)
- **from:** CE-6, session 2026-11-01b

## INV-93: hk comment's window rests on the session's start head (ledger.py::foreign_range), so a session that never runs hk run leaves its commits uncommented

- **affects:** every repo running the engine
- **why not eliminated:** tier 0 has no other cheap anchor (DEC-137)
- **control:** collective: orient's Housekeeping owed line and procedures § Housekeeping, shown to every session
- **from:** CE-6, session 2026-11-01b

## INV-94: zanzibar's main checkout runs under core.autocrlf=true, so a later checkout rewrites CRLF and stales its content-addressed gate rows (a false red, never a false green)

- **affects:** every adopting repo checked out with core.autocrlf=true; zanzibar's main checkout today
- **why not eliminated:** a clone's git config is per clone and the owner's, and an eol attribute changes the owner's whole tree (DEC-94), so init only warns (DEC-270)
- **control:** individual: bootstrap.py::eol_warnings, kit README § 1/§ 2a, gate.md's line-endings row; rerunning the gate restores coverage
- **from:** CE-167, session 2026-11-04a

## INV-95: an adopter's stored index.md goes stale until someone acts on orient's notice

- **affects:** every adopting repo (its context.toml sets `decision_index` and it holds a stored index), the owner and anyone reading the records on GitHub without the CLI, the next session (the `hk_regen_index` tool and the stored index are gone)
- **why not eliminated:** deleting a tracked file in another repo is that repo's owner's call, not the engine's
- **control:** individual: orient's `Deprecated config` section (DEC-160)
- **from:** CE-185, session 2026-11-06a

## INV-96: the published site is only as current as the last deploy, and a failed deploy shows only in GitHub Actions

- **affects:** every adopting repo (its context.toml sets `decision_index` and it holds a stored index), the owner and anyone reading the records on GitHub without the CLI, the next session (the `hk_regen_index` tool and the stored index are gone)
- **why not eliminated:** GitHub runs the deploy, outside the gate
- **control:** collective: the CI watcher every push gets (procedures § Push and CI)
- **from:** CE-185, session 2026-11-06a

## INV-97: (retired 2026-11-06c: a duplicate of INV-95, DEC-162) an adopter's stored decision index.md goes stale until someone acts on orient's Deprecated config notice

- **affects:** every adopting repo that sets decision_index
- **why not eliminated:** deleting a tracked file in another repo is that repo's owner's call, not the engine's
- **control:** individual: orient's Deprecated config section (DEC-160)
- **from:** CE-185, session 2026-11-06a
- **retired:** session 2026-11-06c (claude-code/claude-opus-5-5): a reworded duplicate of INV-95 (DEC-162); kept so its id is never reused

## INV-98: a successor story confirmed by hand in the words that confirmed the story it replaces passes lint: record confirm refuses those words only at the write, and G-I2 does not re-check them

- **affects:** the owner, whose confirmations record their words; any session confirming a story by hand
- **why not eliminated:** a G-I2 re-check was judged not worth building for the by-hand path alone (DEC-162)
- **control:** individual: working.py::Engine.confirm refuses them at the write; by hand, manual-mode § context-engine record confirm
- **from:** CE-163, session 2026-11-06c

## INV-99: An engine older than CE-195 reads a banner: kept close as a stale banner (G-W1 red)

- **affects:** adopters running mixed engine versions
- **why not eliminated:** the receipt is new, and old engines cannot know it
- **control:** individual: RELEASE-NOTES says every machine on the repo needs this engine or later
- **from:** CE-195, session 2026-11-06f

## INV-100: Local commit 3219e82 carries three Sabotage: lines that git parses as trailers

- **affects:** anyone reading 3219e82's trailers
- **why not eliminated:** rewriting history in a shared tree was not asked for
- **control:** individual: DEC-172; commits after 77ac0b7 keep Sabotage lines as body
- **from:** CE-197, session 2026-11-07a

## INV-101: CE_CO_AUTHOR set in a human's environment still adds a Co-Authored-By line

- **affects:** humans running the engine
- **why not eliminated:** first-hit-wins precedence puts the env var above the actor
- **control:** individual: --co-author none / unset CE_CO_AUTHOR (manual-mode § context-engine commit)
- **from:** CE-197, session 2026-11-07a

## INV-102: Hand edits of decision_status that lint does not catch: PROVISIONAL to BUILT/REJECTED/DEFERRED, ACCEPTED back to PROVISIONAL, an owner decision set to anything

- **affects:** anyone editing decision records by hand
- **why not eliminated:** pre-existing (the 0.5 engine caught none either); only an agent call set ACCEPTED by hand is G-W4 now
- **control:** individual: contract § Rules, never hand-edit decision_status
- **from:** CE-187, session 2026-11-07d

## INV-103: decision set moves an owner's own decision from ACCEPTED to PROVISIONAL; nothing refuses it

- **affects:** agents using decision set
- **why not eliminated:** decision_set predates born-ACCEPTED and was not in scope
- **control:** individual: decision accept --owners sweeps it back
- **from:** CE-187, session 2026-11-07d

## INV-104: The 0.6 contract says never accept by hand, while manual-mode gives a by-hand accept fallback (DEC-20)

- **affects:** agents in manual mode
- **why not eliminated:** rewording costs another contract bump
- **control:** individual: the existing never-hand-edit-what-an-op-owns convention; manual-mode § context-engine decision accept
- **from:** CE-187, session 2026-11-07d

## INV-105: manual-mode § orient still omits seven parts orient emits, so a by-hand orient misses them

- **affects:** agents in manual mode
- **why not eliminated:** outside CE-156's list
- **control:** individual: CE-200
- **from:** CE-156, session 2026-11-07d

## INV-106: ask_options' placeholder clause is untested: a sabotage of it stayed green

- **affects:** owner-question refusals
- **why not eliminated:** found by the final verifier, after PASS
- **control:** individual: CE-201
- **from:** CE-158, session 2026-11-07d

## INV-107: A bold intro with its list indented under it reads as one option (a known false refusal)

- **affects:** agents writing owner questions
- **why not eliminated:** by design, DEC-175 amended
- **control:** individual: manual-mode § ask new says to write the list at the bold line's column
- **from:** CE-158, session 2026-11-07d

## INV-108: In full lint G-D11 reports a record that does not parse a second time, though the runbook says every other guard passes over it

- **affects:** anyone reading lint output
- **why not eliminated:** cosmetic, found after PASS
- **control:** individual: manual-mode § context-engine lint
- **from:** CE-161, session 2026-11-07d

## INV-109: A NOW item that does not parse drops out of the G-W5 caps, so lint can add a misleading NOW-short failure beside its schema failure

- **affects:** anyone reading lint output
- **why not eliminated:** the skip is whole-run by design (DEC-176)
- **control:** individual: the schema failure names the file first
- **from:** CE-161, session 2026-11-07d

## INV-110: lint --working now reads every record whole: 5.4s more on this tree (measured 2026-11-07)

- **affects:** sessions running lint --working
- **why not eliminated:** the parse check is what makes the skip visible
- **control:** individual: only the lint op calls it; orient does not
- **from:** CE-161, session 2026-11-07d

## INV-111: Through the CLI and MCP, '; committed <sha>' lands after the WARNING on line 1, so AC-186's 'ends its first line with' holds exactly only for the Engine reply

- **affects:** anyone parsing the close reply
- **why not eliminated:** found after PASS; cosmetic
- **control:** individual: the WARNING text is unchanged and still on line 1
- **from:** CE-191, session 2026-11-07d

## INV-112: With housekeeping, a close whose hk close emptied NOW says G-W5 twice (line-1 WARNING and the hk block)

- **affects:** anyone reading the close reply
- **why not eliminated:** found after PASS; cosmetic
- **control:** individual: both carry the same remedy
- **from:** CE-191, session 2026-11-07d

## INV-113: ask answer and a demoting promote share the fixed board read but only close is tested with an unparseable sibling record

- **affects:** those two ops
- **why not eliminated:** found after PASS
- **control:** individual: the shared Engine._now_refill path is tested through close
- **from:** CE-191, session 2026-11-07d

## INV-114: working.py::Engine._criterion_prefixes shares its name with store.py::Store._criterion_prefixes, which works differently (upper-cased set read by regex over the whole file); a later editor may confuse them

- **affects:** later editors of working.py and store.py
- **why not eliminated:** renaming one is a cheap follow-up not worth widening a tiny task
- **control:** individual: reviewer awareness; the two have different return shapes
- **from:** CE-160, session 2026-11-07e

## INV-115: CE-160's prefix check ignores logged criterion.new ids when the criteria table is empty: if every row was deleted, any prefix is accepted even though the log holds AC ids

- **affects:** owner of a repo whose criteria were all deleted
- **why not eliminated:** needs every row deleted, a rare state, and the remedy (a foreign prefix) is the CE-42 failure it narrows
- **control:** individual: criterion new without --id still derives the prefix from rows, and lint flags mixed series
- **from:** CE-160, session 2026-11-07e

## INV-116: CE-157 release-notes wording is slightly loose: 'from a pin before 2026-10-30' omits that CE-44 (10f8717) and CE-107 (55c47ec) both landed late on 2026-10-30, so an earlier-that-day pin is also affected; and 'kit README section 3 step 4' is the import step, the upgrade procedure is section 4 (the task text cited section 3 step 4)

- **affects:** adopters upgrading from a pin taken on 2026-10-30
- **why not eliminated:** a wording nit in release notes, adopters pinning mid-day 2026-10-30 are the only ones misled
- **control:** individual: fix the lines at the 0.6 release edit; the notes are reviewed by the owner at release
- **from:** CE-157, session 2026-11-07e

## INV-117: kit README § 3 says 'Only index.md and log.md are exempt', but store.py::Store.lint_bundles exempts index.md from needing a type yet still fails one with frontmatter beyond okf_version, so the wording is loose

- **affects:** adopters reading the kit README
- **why not eliminated:** wording slightly loose, does not change behaviour or block adopters
- **control:** individual: kit README § 3 text, read by the adopter
- **from:** CE-180, session 2026-11-07e

## INV-118: the CE-180 test checks only that the RESERVED_MD names appear in kit README § 3, not that § 3 calls them exempt

- **affects:** maintainers editing the kit README
- **why not eliminated:** a doc test of presence, not of claim; the claim is not mechanically pinned
- **control:** individual: tests/test_kit.py README section check
- **from:** CE-180, session 2026-11-07e

## INV-119: task new --body-file test does not pin cli::_read's CRLF-to-LF step: a sabotage to read_bytes().decode('utf-8-sig') still passed, because the test reads the body back through the okf store, which normalises line endings, not the file bytes on disk

- **affects:** engine maintainers
- **why not eliminated:** real code is correct (read_text translates newlines); the test asserts only through the store
- **control:** individual: test_working.py test of task new --body-file (the 'not in got' CR check, weak)
- **from:** CE-174, session 2026-11-07e

## INV-120: tools/linux_gate.py (CE-67) was not run for this change

- **affects:** whoever pushes next
- **why not eliminated:** it is a pre-push step and nothing was pushed
- **control:** individual: CLAUDE.md § Gate pre-push rule and tools/linux_gate.py
- **from:** CE-174, session 2026-11-07e

## INV-121: DEC-179, DEC-180 and DEC-181 are PROVISIONAL (actor claude-code/claude-sonnet-5-5) and await owner review

- **affects:** owner
- **why not eliminated:** agent calls stay PROVISIONAL until the owner accepts them
- **control:** individual: context-engine decision accept after owner review
- **from:** CE-174, session 2026-11-07e

## INV-122: The DEC-175 amendment has its dated header twice and the inner date (2026-11-08) does not match the session label; meaning intact

- **affects:** readers of DEC-175
- **why not eliminated:** a record correct by a later session cleans it; the verifier writes no record
- **control:** individual: record correct on DEC-175
- **from:** CE-201, session 2026-11-07e

## INV-123: Builder sabotages S2 (max by len), S3 (sub = len(indent)), S4 (message and remedy reverts) were checked by reading the code, not re-run

- **affects:** maintainers trusting the guard
- **why not eliminated:** S1-class behaviour was re-run first-hand with a different sabotage and each goes red for the stated reason
- **control:** individual: the sabotage rule (CLAUDE.md, DEC-11) and the pinned tests in tests/test_working.py
- **from:** CE-201, session 2026-11-07e

## INV-124: Shape-1 false pass stays by design: a bold option with unindented bullets reads as those bullets

- **affects:** owners asking questions in that shape
- **why not eliminated:** DEC-175 reopen condition; judged not worth a rule
- **control:** reduce: pinned test and the 'Not checked' notes in guards.py::ask_options and guards.py::ask_problems
- **from:** CE-201, session 2026-11-07e

## INV-125: _orient_titles comment and commit message say '22 on 2026-11-08' but len(found) is 23 (22 distinct headings, Top item twice); the floor of 20 leaves 3 titles of slack, so up to 3 titles could move to a form the regex misses with no test red

- **affects:** the next session editing orient titles or manual-mode § orient
- **why not eliminated:** a floor with slack avoids a brittle exact count; a stricter floor was not worth the churn
- **control:** individual: tests _orient_titles floor of 20
- **from:** CE-200, session 2026-11-07e

## INV-126: the parked-items line format in manual-mode § orient shows a single dep, but working.py::Engine.parked_deps joins several deps with '; '

- **affects:** a by-hand session reading the manual-mode orient description
- **why not eliminated:** doc example kept to the common single-dep case
- **control:** individual: none beyond review of manual-mode § orient
- **from:** CE-200, session 2026-11-07e

## INV-127: orient part ranks and rest pointers are described in prose but pinned by no test (DEC-184, as planned)

- **affects:** the next session changing orient order or pointers, and by-hand sessions relying on the prose
- **why not eliminated:** DEC-184 chose prose over a pin
- **control:** individual: DEC-184
- **from:** CE-200, session 2026-11-07e

## INV-128: The refusal path through Store.new is not tested; T2 tests only derivation and no engine caller reaches that refusal today

- **affects:** a future caller of Store.new that passes a contradicting status
- **why not eliminated:** no caller reaches the refusal so a test was not required by the plan
- **control:** reduce: tests/test_store.py derivation test (T2)
- **from:** CE-179, session 2026-11-07e

## INV-129: AC-189 'its other keys unchanged' is not asserted directly; only the doc state/status and the caller-dict-unchanged asserts cover it

- **affects:** a change to derivation that alters other keys unnoticed
- **why not eliminated:** indirect asserts were judged enough by the verifier
- **control:** reduce: tests/test_store.py caller-dict-unchanged and doc state/status asserts
- **from:** CE-179, session 2026-11-07e

## INV-130: DEC-186..188 are not linked to CE-179 by decision link

- **affects:** a reader tracing CE-179 to its decisions
- **why not eliminated:** the plan did not require it
- **control:** individual: commit titles and the CE-179 close commit cite DEC-186..188
- **from:** CE-179, session 2026-11-07e

## INV-131: Fence exclusion not pinned: stripping fence markers before table_blocks in _criterion_ids left the AC-160 test green, and before criteria_rows in _criteria_read left the AC-40 test green, since each fence holds one row

- **affects:** engine maintainers
- **why not eliminated:** low risk because fence skipping lives in guards.py::prose which lint shares; fix is a header, separator and row inside the fence
- **control:** reduce: the AC-160 and AC-40 tests in tests/ (weak on fences)
- **from:** CE-150, session 2026-11-07e

## INV-132: Changed AC-70 assertion in tests/test_intent.py stays green if _criteria_read returns the old raw row regex, as the chain fixture has no row the two parsers disagree on

- **affects:** engine maintainers
- **why not eliminated:** the new AC-40 test covers that difference instead
- **control:** reduce: AC-40 test and tests/test_intent.py AC-70 assertion
- **from:** CE-150, session 2026-11-07e

## INV-133: manual-mode.md § context-engine decision link (both kit copies) describes the criterion check more loosely than the engine applies it; a by-hand follower could link AC-13 (table with no status column) or an id inside a fence, which the engine refuses; no lint guard checks criterion links in amends

- **affects:** manual-mode users and runbook readers
- **why not eliminated:** runbook wording not yet tightened and no lint guard; follow-on
- **control:** individual: the engine refusal in decision link
- **from:** CE-150, session 2026-11-07e

## INV-134: decision link hint is built from the first criteria_rows problem of any kind, possibly unrelated to the target table; a duplicate-id problem reads as 'lint cannot read part of'

- **affects:** engine users reading the hint
- **why not eliminated:** wording slightly off, behaviour right
- **control:** individual: the refusal itself still fires correctly
- **from:** CE-150, session 2026-11-07e

## INV-135: With the superset counting, --id AC-n is refused with 'already leads a row of <criteria>' when AC-n leads a row of a table that is not a criteria table; correct under P3 but the message does not name the table

- **affects:** engine users allocating ids
- **why not eliminated:** message lacks the table name
- **control:** individual: the refusal in id allocation
- **from:** CE-150, session 2026-11-07e

## INV-136: store.py::Store._criterion_prefixes still uses its own raw regex (DEC-191), and tools/sabotage_ce5.py is stale in exactly the 5 named rows at parent 49af3b3 and at a77a9d1 (DEC-192)

- **affects:** engine maintainers
- **why not eliminated:** confirmed follow-ons, deliberately not done here
- **control:** individual: DEC-191 and DEC-192 record them
- **from:** CE-150, session 2026-11-07e

## INV-137: DEC-194 claim that a missing id stays listed in the pause-resume hint is not pinned by a test (filter changed to state not in closed/missing kept T3 and T4 green; probe shows the code is right)

- **affects:** engine maintainers
- **why not eliminated:** the plan did not ask for this test and the code is correct today
- **control:** reduce: none yet, a test pinning a hand-added missing id in the hint would guard it
- **from:** CE-152, session 2026-11-07e

## INV-138: ask raised refusal remedy (say in the close digest that it was raised) dead-ends for a NOW/NEXT Ask- question because working.py::Engine.session_close still refuses with the asked receipt does not name Ask-1 (its check also uses ID_RE)

- **affects:** sessions closing with a raised NOW/NEXT Ask- question
- **why not eliminated:** predates this change and the remedy text was pinned by the plan
- **control:** reduce: session_close refusal and its own remedy, demoting the question to LATER
- **from:** CE-152, session 2026-11-07e

## INV-139: the new pause_resume hint reply is tested only through the Python API, no CLI or MCP test covers it (ops.py::pause_resume passes the string through unchanged)

- **affects:** engine maintainers
- **why not eliminated:** pass-through is trivial and the plan asked only for the API test
- **control:** reduce: tests/test_working.py API tests of pause_resume
- **from:** CE-152, session 2026-11-07e

## INV-140: a housekeeping resume of a landed pause now also prints the open-tasks hint, so a session could name tasks it was not asked for

- **affects:** sessions resuming a landed pause
- **why not eliminated:** the hint is wanted on every resume and cannot know the pause landed
- **control:** individual: the hint wording (if you take up its request)
- **from:** CE-152, session 2026-11-07e

## INV-141: Engine._comment_problem calls Engine._board(), which raises a Refusal ('[working] names no board kinds') in a repo with no board kinds; reachable only through single-item hk_comment

- **affects:** an operator running hk_comment in a repo without board kinds
- **why not eliminated:** edge case outside any board-using repo, and the refusal carries a sensible remedy
- **control:** individual: the Refusal text from Engine._board names the fix
- **from:** CE-170, session 2026-11-07e

## INV-142: The brief's 'record new decision --file' form needs '--set actor=' (a template or engine-default question outside CE-170)

- **affects:** an agent following the brief verbatim
- **why not eliminated:** out of CE-170 scope, not yet decided whether template or engine default should supply actor
- **control:** individual: the refusal on a missing actor names the flag
- **from:** CE-170, session 2026-11-07e

## INV-143: freeze refuses a doc whose H1 falls outside G-D4's window even when 'first after its frontmatter' would fit (frontmatter of about 7-8 lines, then H1 and a blank)

- **affects:** adopters freezing a doc with long frontmatter
- **why not eliminated:** the spec says refuse rather than fall back
- **control:** individual: the post-check in working.py::Engine.doc_freeze refuses and writes nothing; the adopter places the line by hand per manual-mode
- **from:** CE-172, session 2026-11-07e

## INV-144: freezing a doc of '# D\n', '# D' or '' leaves it ending in a blank line

- **affects:** adopters freezing near-empty docs
- **why not eliminated:** spec-intended, cosmetic
- **control:** individual: tests/test_docs.py cases g and h pin the result
- **from:** CE-172, session 2026-11-07e

## INV-145: half of the doc_freeze post-check is unpinned: weakening it to got.word != 'FROZEN' (dropping the line comparison) leaves every test green

- **affects:** a future change to doc_freeze that makes the branch reachable
- **why not eliminated:** that half cannot be reached today, so it is extra protection
- **control:** individual: none beyond the other half of the post-check, which is pinned by test_freeze_refuses_what_it_cannot_freeze_and_writes_nothing
- **from:** CE-172, session 2026-11-07e

## INV-146: The null and ~ spellings of an empty stale_after are not tested separately from the empty string

- **affects:** engine maintainers
- **why not eliminated:** they take the same store.py::coerce path as the tested empty-string case
- **control:** reduce: test_record_new_task_set_and_decision_set_refuse_a_bad_or_expired_stale_after[empty-*]
- **from:** CE-155, session 2026-11-07e

## INV-147: Timestamp forms YAML might read but fromisoformat rejects (lowercase t or z) are refused at write time

- **affects:** record writers using unusual timestamp spellings
- **why not eliminated:** refusing is safe, since lint's guards.py::instant would be red on the stored string anyway
- **control:** reduce: guards.py::instant via lint G-D4
- **from:** CE-155, session 2026-11-07e

## INV-148: The CLI test for task set checks only that stale_after appears in stderr, not the reason

- **affects:** engine maintainers
- **why not eliminated:** the engine-level tests pin the reasons
- **control:** reduce: test_record_new_task_set_and_decision_set_refuse_a_bad_or_expired_stale_after
- **from:** CE-155, session 2026-11-07e

## INV-149: the write-time check is stricter than lint for deprecated records (retire's reason; amend/correct/confirm on a superseded decision): it refuses text lint at rest would never fail; undecided whether those ops should skip the check or keep it

- **affects:** an agent retiring or amending a deprecated record who must reword
- **why not eliminated:** not decided; keeping the check is the safe side
- **control:** individual: the write-time G-D3 twin refusal in the append-only ops
- **from:** CE-183, session 2026-11-07e

## INV-150: record new without --id refuses a body that cites the id it is about to get; by design, own is only the rid passed in

- **affects:** an agent recording owner words that cite their own new id
- **why not eliminated:** by design, the id is not known before the write
- **control:** individual: the write-time G-D3 twin refusal, which names the remedy (pass --id)
- **from:** CE-183, session 2026-11-07e

## INV-151: no criteria row (AC-n) claims the CE-183 tests, so no criterion tracks the write-time twin

- **affects:** the owner reading the criteria register
- **why not eliminated:** criterion not yet written
- **control:** individual: none beyond the tests themselves
- **from:** CE-183, session 2026-11-07e

## INV-152: .scratch/wave-2026-11-07e/ce-183/ still holds probes, logs and sabotage scripts (verifier_r3_sabotage.py among them), gitignored and unrecorded

- **affects:** the next session reading .scratch
- **why not eliminated:** the coordinator must transcribe or delete them
- **control:** individual: none; housekeeping
- **from:** CE-183, session 2026-11-07e

## INV-153: H3_RE's alternative for a bare ### line (the |$ branch in decisions.py::H3_RE) is unpinned: the verifier's sabotage dropping it stayed green

- **affects:** decision import of a log whose only headings are bare ###
- **why not eliminated:** the bare-### case in an entry-less log has no test of its own
- **control:** reduce: tests/test_decisions.py CE-171 block pins the spaced ### form only
- **from:** CE-171, session 2026-11-07e

## INV-154: ea3ddb4's message and the builder summary cite Working.import_log, which does not exist (the class is Engine); the commit is immutable

- **affects:** a reader following the citation
- **why not eliminated:** a commit message cannot be amended after the fact
- **control:** reduce: CE-202 comment records working.py::Engine.import_log
- **from:** CE-171, session 2026-11-07e

## INV-155: DEFERRED decisions counting as current by G-I4 has no committed test (verifier probe: DEFERRED+PROVISIONAL with tab vs space fires once)

- **affects:** engine maintainers
- **why not eliminated:** verifier probe only, not pinned in tests/test_guards.py
- **control:** individual: G-I4 guards.py::decision_titles
- **from:** CE-189, session 2026-11-07e

## INV-156: CE-189 log comment says 'uncommitted', now out of date after bd25ca2

- **affects:** readers of the board log
- **why not eliminated:** board log is append-only; this close message supersedes it
- **control:** individual: close commit bd25ca2 and this close
- **from:** CE-189, session 2026-11-07e

## INV-157: Full gate takes about 600s (598.6s measured 2026-11-07), at the Bash foreground limit

- **affects:** sessions running the gate
- **why not eliminated:** suite size, not a defect of this change
- **control:** individual: run gate with run_in_background
- **from:** CE-189, session 2026-11-07e

## INV-158: DEC-214 to DEC-217 are PROVISIONAL and await owner review

- **affects:** owner
- **why not eliminated:** agent calls stay PROVISIONAL until owner accepts
- **control:** individual: context-engine decision accept after owner review
- **from:** CE-189, session 2026-11-07e

## INV-159: the session close refusal remedy text (fit gate_receipt to the result line, or '') is not pinned by any test; the test asserts only 'pass count' and 'gate_receipt', which the old remedy also contained

- **affects:** engine maintainers
- **why not eliminated:** low-value text pin, the behaviour itself is tested
- **control:** reduce: none yet; pin the new remedy wording in tests/test_working.py
- **from:** CE-192, session 2026-11-07e

## INV-160: the tests/test_kit.py parity assert checks only the C.Working() dataclass default; the load path for an absent gate_receipt key is guarded only by the AC-125 test (sabotage: absent key read as '' in config.py::from_dict turned AC-125 red and left test_kit green)

- **affects:** engine maintainers
- **why not eliminated:** one guard covers it, but only indirectly
- **control:** reduce: AC-125 test
- **from:** CE-192, session 2026-11-07e

## INV-161: decision commits b33560d..7dfd1ba precede code commit 261e538, so DEC-223 cites config.py::GATE_RECEIPT before it exists in history

- **affects:** readers bisecting history
- **why not eliminated:** lint is not affected (decisions are not in [guards] links, G-D3); history order only
- **control:** individual: G-D3
- **from:** CE-192, session 2026-11-07e

## INV-162: ops.py::session_close (the MCP docstring) does not describe the guards receipt rule; true before CE-192 as well

- **affects:** MCP tool users
- **why not eliminated:** doc gap in tool help, not behaviour
- **control:** reduce: none
- **from:** CE-192, session 2026-11-07e

## INV-163: the default gate_receipt takes effect on upgrade in adhoc (CE-166), which is outside this repo and needs an adhoc session

- **affects:** adhoc repo sessions
- **why not eliminated:** intended effect, but not verifiable from here
- **control:** individual: CE-166
- **from:** CE-192, session 2026-11-07e

## INV-164: no test edits the archive file (dest) mid-run: removing dest from Engine.doc_archive's seen snapshot kept tests/test_docs.py green

- **affects:** engine maintainers
- **why not eliminated:** the plan's T5 did not ask for this case, so the snapshot of dest is unpinned
- **control:** individual: review of Engine.doc_archive; the other mid-run cases are tested
- **from:** CE-154, session 2026-11-07e

## INV-165: the FROZEN safety net in Engine.doc_archive refuses even when G-D4 is off or does not read the archive dir; a pathological liveness_lines of 1 would refuse every frontmatter doc

- **affects:** repos with unusual guard config
- **why not eliminated:** the net is unconditional by design
- **control:** individual: the refusal names its remedy; default liveness_lines is not pathological
- **from:** CE-154, session 2026-11-07e

## INV-166: a whole move whose relative link was already red, but whose message changes when resolved from the archive dir, is still named as new by doc archive

- **affects:** owners archiving docs with already-red links
- **why not eliminated:** the planner accepted this; pointer reds compare messages without line numbers only
- **control:** individual: the refusal text and the by-hand runbook step
- **from:** CE-154, session 2026-11-07e

## INV-167: a prune can drop an ACTIVE-PLAN doc's named board item out of G-D4's window (G-D4 red); doc archive --lines does not check it

- **affects:** owners pruning active-plan docs
- **why not eliminated:** not checked by the build
- **control:** individual: gate/lint G-D4 reports it after the prune
- **from:** CE-154, session 2026-11-07e

## INV-168: a small TOCTOU window remains between doc archive's re-check (DEC-228) and its first write

- **affects:** concurrent sessions in one tree
- **why not eliminated:** no file lock is taken
- **control:** individual: DEC-228 re-check narrows it; lint after the archive catches damage
- **from:** CE-154, session 2026-11-07e

## INV-169: a hand edit on top of an engine-written, still uncommitted redirect table or archive file passes DEC-227's check

- **affects:** concurrent sessions in one tree
- **why not eliminated:** op lines carry no content hash
- **control:** individual: the check refuses hand edits to committed state; commit eagerly after an archive
- **from:** CE-154, session 2026-11-07e

## INV-170: Stale G-n text is left in working.py::Engine._story_checks (remedy says goals=[G-n, ...], and its docstring) and in the ops.py::task_new docstring, which is also the MCP tool's description; the problem message names the right spelling

- **affects:** an agent reading the remedy or the MCP tool description
- **why not eliminated:** wording only, not blocking, the message itself carries the right spelling
- **control:** individual: the problem message in working.py::Engine._story_checks
- **from:** CE-56, session 2026-11-07e

## INV-171: Lint checks the reserved prefixes EXP and HAZ on the [working] task kind only, so another kind could take EXP or HAZ without a lint red

- **affects:** an adopter who gives a non-task kind the prefix EXP or HAZ
- **why not eliminated:** the plan pinned the task kind only, though the title says reserved prefixes in lint
- **control:** reduce: lint G-D2 on the task prefix
- **from:** CE-56, session 2026-11-07e

## INV-172: A register mixing prefixes with distinct numbers (INV-1, RISK-2) is not a lint red; only the next filing refuses

- **affects:** an adopter whose register carries two prefixes
- **why not eliminated:** lint does not see the mix until a filing hits it
- **control:** collective: review.py::series refuses the next filing
- **from:** CE-56, session 2026-11-07e

## INV-173: working.py::Engine._register_issued takes the last prefix from op-log line order, and a union-merged op log is not chronological across branches

- **affects:** a repo merging branches that each filed register entries
- **why not eliminated:** merge order is outside the engine's control
- **control:** individual: review.py::series refuses a mixed next filing
- **from:** CE-56, session 2026-11-07e

## INV-174: After an upgrade, adopted repos get G-D0 drift on their runbooks until they recopy them

- **affects:** adopted repos upgrading the engine
- **why not eliminated:** the normal upgrade flow, not a contract change
- **control:** collective: lint G-D0 names the drift and the fix
- **from:** CE-56, session 2026-11-07e

## INV-175: tools/linux_gate.py was not run for this work; it is only needed before a push

- **affects:** the session that pushes this work
- **why not eliminated:** CI parity check is a push-time step
- **control:** collective: CLAUDE.md § Gate requires tools/linux_gate.py before every push
- **from:** CE-56, session 2026-11-07e

## INV-176: token figures leave out cache_read and were matched to the CE-191 comment and the opus baselines by magnitude only; the CE-195/197 baseline convention is not re-measurable

- **affects:** the owner ruling on DEC-45
- **why not eliminated:** the baselines were recorded before any helper script and their transcripts were not re-summed
- **control:** individual: per-task comments on CE-198 and the no-close like-for-like comparison
- **from:** CE-198, session 2026-11-07e

## INV-177: the trial's tasks were pinned small tasks, and opus-with-planner tasks outside it ran a median 547k (trial -25.9% against them), so the 30% margin may not hold on a mixed population

- **affects:** the owner ruling on DEC-45
- **why not eliminated:** eligibility selects the tasks, and no same-task opus control exists
- **control:** individual: DEC-173 size floor and the eligibility filter
- **from:** CE-198, session 2026-11-07e

## INV-178: ledger.py::Entry.receipt matches the first '  - pushed:' line anywhere in an entry, so a summary or Still-owed bullet starting 'pushed: <sha>' would clear the flag without validation (no such line in the ledger today)

- **affects:** orient push flag readers
- **why not eliminated:** every receipt shares this parse; none is in the ledger today
- **control:** collective: ledger.py::Entry.receipt first-match rule
- **from:** CE-176, session 2026-11-07e

## INV-179: a whitespace-only --pushed skips working.py::Engine._pushed_receipt but ledger.py::render_close still writes an empty pushed: line (asked behaves the same)

- **affects:** session close callers
- **why not eliminated:** low impact, empty receipt is visible in the ledger
- **control:** reduce: working.py::Engine._pushed_receipt
- **from:** CE-176, session 2026-11-07e

## INV-180: a pushed receipt written by hand in manual mode is checked by no lint guard (G-W6 unchanged by the plan)

- **affects:** manual-mode sessions
- **why not eliminated:** manual-mode fallback is rare and the entry is reviewed by hand
- **control:** individual: docs/runbooks/manual-mode.md pushed receipt step
- **from:** CE-176, session 2026-11-07e

## INV-181: tools/sabotage_ce185.py's runner counts a row red on any non-zero pytest exit code and does not check the reason, so 'ALL RED' is weaker than sabotage_ce55's verdict check

- **affects:** future sabotage-row authors
- **why not eliminated:** pre-existing before CE-186; the verifier re-ran each new row with a fresh PYTHONPYCACHEPREFIX and each went red for the right reason
- **control:** collective: the sabotage rule in CLAUDE.md (hand check of each row's red reason)
- **from:** CE-186, session 2026-11-07e

## INV-182: manual-mode.md kinds table: the question row still says 'as task', which now reads as if the question pri includes HOLD, against the context.toml.template

- **affects:** an adopter reading the by-hand runbook
- **why not eliminated:** wording left unqualified in the by-hand runbook
- **control:** collective: kit and repo runbook byte-equality gate keeps copies in step, but nothing checks the wording
- **from:** CE-188, session 2026-11-07e

## INV-183: FRAMEWORK.md section 5.2 sprint bullet and the section 6.14 intro read 'every open item' without 'not at HOLD' (step 1 and the Ranking line are qualified)

- **affects:** a reader of the spec following the sprint bullet
- **why not eliminated:** prose left unqualified
- **control:** collective: FRAMEWORK section 6.14 step 1 and the Ranking line state the HOLD exemption
- **from:** CE-188, session 2026-11-07e

## INV-184: working.py::_unheld filters by pri regardless of kind, so an adopter who adds HOLD to the question pri enum gets held questions the docs say cannot exist, and nothing refuses it

- **affects:** adopters who customise the question pri enum
- **why not eliminated:** HOLD is optional per kind and config validation does not tie a tier to a kind
- **control:** reduce: docs say HOLD belongs to the task kind only; test_hold_is_on_the_task_kind_only_in_the_kit_and_here pins this repo and the kit template
- **from:** CE-188, session 2026-11-07e

## INV-185: orient's Top item on a held-only board says only 'no NOW item' and gives no hint that only held items remain

- **affects:** a session starting on a board where every open task is held
- **why not eliminated:** message wording not reworked in this task
- **control:** collective: task list shows held items last; the owner reads the board
- **from:** CE-188, session 2026-11-07e

## INV-186: DEC-244, DEC-245, DEC-246 are PROVISIONAL and the owner has not reviewed them or made the rank call on moving this repo's SOMEDAY items to HOLD

- **affects:** the owner
- **why not eliminated:** owner review and a rank call are the owner's, not an agent's
- **control:** individual: PROVISIONAL decision status and the close digest flag; decision accept after review
- **from:** CE-188, session 2026-11-07e

## INV-187: the verifier's sabotage runs (verifier_sab.py, verifier_sab.log) exist only in gitignored .scratch/wave-2026-11-07e/ce-188/

- **affects:** a later auditor wanting the verifier's own runs
- **why not eliminated:** the runs are evidence kept outside any tracked file
- **control:** collective: the builder's Sabotage lines in commit 3787b49 record the same breakages in tracked history
- **from:** CE-188, session 2026-11-07e

## INV-188: Engine.section matches the name exactly: task section ASK-n 'Grant ' (or ' Grant' or 'grant') writes a second look-alike heading; the hashed words and G-W4 are unaffected, but the record carries a confusing duplicate

- **affects:** anyone reading the ASK record
- **why not eliminated:** not worth a guard for a hand-typed near-duplicate heading
- **control:** reduce: G-W4 and the hashed words are unaffected
- **from:** CE-190, session 2026-11-07e

## INV-189: If the stub closes between _grant_check and _stub_granted, the question is already closed with no granted: line; the remedy says to quote by hand

- **affects:** the session granting
- **why not eliminated:** a narrow race between two engine steps
- **control:** individual: the refusal remedy tells the operator to quote the grant by hand
- **from:** CE-190, session 2026-11-07e

## INV-190: Owner words cannot be stored with a '## ' line; such an answer must go as a decision (documented)

- **affects:** the coordinator recording owner words
- **why not eliminated:** a '## ' line would be read as a section heading in the append-only record
- **control:** individual: documented in manual-mode and procedures; the answer goes as a decision
- **from:** CE-190, session 2026-11-07e

## INV-191: DEC-247..250 are PROVISIONAL and await owner review; the MCP server is stale until Claude Code restarts

- **affects:** the owner
- **why not eliminated:** agent calls stay PROVISIONAL until the owner reviews them; the MCP server is loaded once per Claude Code start
- **control:** individual: decision accept after owner review; CLI used until restart
- **from:** CE-190, session 2026-11-07e

## INV-192: review.py::retire on an entry with an empty risk writes a heading with no space after the colon and a trailing space

- **affects:** the register reader
- **why not eliminated:** cosmetic only; such an entry is already G-W13 red (names no risk)
- **control:** individual: G-W13 flags an entry that names no risk
- **from:** CE-196, session 2026-11-07e

## INV-193: A non-entry '## ' section after the last register entry falls inside that entry's block in review.py::entries and review.py::_add_line

- **affects:** whoever edits the register by hand
- **why not eliminated:** a '- **x:**' line in that section would be read as the entry's last field; no such section exists today
- **control:** individual: the register file layout keeps entries last
- **from:** CE-196, session 2026-11-07e

## INV-194: working.py::Engine.lint_review picks the remedy by testing each entry_problems message for the substring 'retired'

- **affects:** the operator reading a lint remedy
- **why not eliminated:** a future problem message quoting risk text could get the wrong remedy
- **control:** individual: tests of lint_review remedies
- **from:** CE-196, session 2026-11-07e

## INV-195: site.py::Site.register_page intro (N residual risks) shows no retired count

- **affects:** the site reader
- **why not eliminated:** the plan did not ask for one
- **control:** individual: register show prints the retired lines
- **from:** CE-196, session 2026-11-07e

## INV-196: INV-90 hand-written retired line has brackets in its why, which the op would refuse

- **affects:** whoever retires an entry by hand
- **why not eliminated:** stylistic difference from the hand form only; heading forms agree and G-W13 is clean on the packaged register
- **control:** individual: G-W13
- **from:** CE-196, session 2026-11-07e

## INV-197: DEC-251..DEC-257 are PROVISIONAL and await owner review

- **affects:** the owner
- **why not eliminated:** agent calls stay PROVISIONAL until the owner reviews them
- **control:** individual: decision accept after owner review
- **from:** CE-196, session 2026-11-07e

## INV-198: The orient notice has no opt-out (DEC-260, PROVISIONAL): an adopter using only the CLI, or a harness other than Claude Code, sees a rank-2 part naming a claude command on every orient

- **affects:** CLI-only adopters and non-Claude-Code harnesses
- **why not eliminated:** the owner chose a notice until a tool call marks the clone, and an opt-out was not built; DEC-260 is PROVISIONAL awaiting owner review
- **control:** individual: DEC-260 owner review; orient notice cleared by the clone mark after one MCP tool call
- **from:** CE-177, session 2026-11-07e

## INV-199: This repo's own orient shows the MCP notice until the stale MCP server is restarted and one tool call reaches the engine

- **affects:** sessions in this repo until the owner restarts Claude Code
- **why not eliminated:** the running MCP server predates the change and restarting Claude Code is the owner's action
- **control:** individual: the clone mark written by the first MCP tool call after restart
- **from:** CE-177, session 2026-11-07e

## INV-200: The extra rank-2 orient part adds bytes; in an adopter with a tight byte cap it could push other rank-2 parts out of orient

- **affects:** adopters with a tight orient byte cap
- **why not eliminated:** the notice is needed until the clone is marked, and its size is bounded but not budgeted against a cap
- **control:** reduce: orient byte cap and rank ordering in working.py; notice disappears once the clone is marked
- **from:** CE-177, session 2026-11-07e

## INV-201: Contract open issue: the 0.6 release notes already say the contract changes, and whether the MCP-server-is-optional wording in kit/contract.md can change within 0.6 or needs 0.7 is undecided; the builder left the contract untouched, so contract wording still calls MCP optional

- **affects:** adopters reading the contract, and the owner
- **why not eliminated:** a framework version rule is the owner's call
- **control:** individual: lint G-D0 keeps contract.md equal to kit/contract.md; owner ruling on 0.6 vs 0.7
- **from:** CE-177, session 2026-11-07e

## INV-202: No test covers a mark-write failure through the MCP tool itself (verifier item E6); only the lower layer is tested

- **affects:** engine maintainers
- **why not eliminated:** a failing mark write is hard to provoke through the stdio tool and the lower-layer test covers the logic
- **control:** reduce: the lower-layer mark-write failure test in tests/test_working.py
- **from:** CE-177, session 2026-11-07e

## INV-203: store.py::coerce turns '', 'null' and '~' into None, so a legacy string 'null' under a typed key (moved) is silently written as an empty value with no as entry, and manual-mode § context-engine task import step 2 does not mention it

- **affects:** an owner importing a legacy board with literal null strings
- **why not eliminated:** a legacy value that reads as null is indistinguishable from a deliberate empty one at import
- **control:** individual: none yet; the runbook step 2 should name the coercion
- **from:** CE-178, session 2026-11-07e

## INV-204: AC-196 and FRAMEWORK §11.4 say 'as is written only by the import' but hk.stamp_asked (working.py, via _board_set as_) also writes as; only the G-W7 bullet names it

- **affects:** a reader of AC-196 or §11.4, and the next session trusting them
- **why not eliminated:** spec wording written before stamp_asked was counted as a second writer
- **control:** individual: the G-W7 bullet in FRAMEWORK names it; AC-196 and §11.4 wording need correcting
- **from:** CE-178, session 2026-11-07e

## INV-205: When create_many refuses on schema (e.g. moved given as a JSON int 20260729) the message names the target file, not the input line or id; only the coerce path names the line

- **affects:** an owner importing a large legacy board
- **why not eliminated:** schema refusal fires after the input row is lost to the batch
- **control:** individual: none; the owner finds the row by value
- **from:** CE-178, session 2026-11-07e

## INV-206: task import trusts kept values as given: no dry run and no tier-cap, deps or goals check at import, and plain dates (zanzibar has 120+) need a key of the repo's own

- **affects:** an owner importing a legacy board such as zanzibar
- **why not eliminated:** import is a one-shot bulk write that mirrors the legacy board verbatim
- **control:** individual: G-W7 and lint run after the import; runbook describes the step
- **from:** CE-178, session 2026-11-07e

## INV-207: tools/sabotage_ce14.py AC-51 row anchors on 'if v != str(op.get("session")):' but guards.py::tool_owned now has 'if v != want:', so the scripted sabotage is stale and cannot go red for AC-51

- **affects:** whoever re-runs sabotage_ce14 to believe AC-51
- **why not eliminated:** the guard was refactored without the script anchor being updated; already stale before CE-178
- **control:** individual: none; the sabotage rule is hand-run until the anchor is fixed
- **from:** CE-178, session 2026-11-07e

## INV-208: bootstrap.py::eol_warnings checks only root/.git, so a root that is a subdirectory of a repo (a monorepo) gets no line-ending warning; commit.py::_in_git_tree already walks the parents

- **affects:** adopters whose context root is a subdirectory of a git repo
- **why not eliminated:** the plan pinned it and the warning is advisory
- **control:** individual: procedures.md bootstrap step and kit README name the per-clone core.autocrlf fix
- **from:** CE-184, session 2026-11-07e

## INV-209: DEC-272 known gaps: core.eol=crlf with a text attribute is not caught, and a .gitattributes pinning only context.toml silences the warning while other files still check out CRLF

- **affects:** adopters with unusual eol config or partial .gitattributes
- **why not eliminated:** recorded as known gaps in DEC-272, advisory warning only
- **control:** individual: DEC-272 and the procedures.md bootstrap step
- **from:** CE-184, session 2026-11-07e

## INV-210: tools/linux_gate.py has not been run for the CE-184 commits; T2 relies on git -c core.autocrlf=true clone converting files on Linux too (git documented behaviour)

- **affects:** the next pusher
- **why not eliminated:** no push was asked for
- **control:** collective: CLAUDE.md Gate section requires tools/linux_gate.py green before every push
- **from:** CE-184, session 2026-11-07e

## INV-211: check_lane runs on every op, reads included, so a malformed CE_AGENT in the environment makes orient and the SessionStart hook refuse

- **affects:** any session started with a malformed CE_AGENT
- **why not eliminated:** validating on every op is the simplest place to catch a bad lane
- **control:** reduce: check_lane refusal names the bad value
- **from:** CE-126, session 2026-11-07e

## INV-212: an unparseable line cut inside the lane value has no closing quote, so commit.py::lane_of finds no lane and the line is filed as the coordinator's

- **affects:** a subagent's torn op line
- **why not eliminated:** a truncated line carries no recoverable lane
- **control:** reduce: lint flags unparseable op lines
- **from:** CE-126, session 2026-11-07e

## INV-213: under EVERY_LANE the close or pause reply and its commit message do not say that a lane's lines went in (commit.py::_others is empty)

- **affects:** the coordinator auditing a close
- **why not eliminated:** reply wording was not extended for lanes
- **control:** individual: the coordinator reads git show of the commit
- **from:** CE-126, session 2026-11-07e

## INV-214: fan-out.md has about 12 bytes left under the G-D1 byte cap

- **affects:** the next edit to fan-out.md
- **why not eliminated:** the one-line CE_AGENT rule used the remaining room
- **control:** reduce: G-D1 byte cap fails the gate on overflow
- **from:** CE-126, session 2026-11-07e

## INV-215: workflow scripts that spawn task agents do not yet pass CE_AGENT=<task id>, so a subagent's lines are still filed as the coordinator's until they do

- **affects:** the coordinator and every fanned-out task
- **why not eliminated:** scripts are outside this task's code scope
- **control:** individual: the fan-out.md one-line rule; coordinator follow-up
- **from:** CE-126, session 2026-11-07e

## INV-216: The end of the operations section is not pinned by a unit test: with spec_items never resetting ops_section after ### 8.0.2, test_guards.py and test_coverage_status.py stay green (the fixture has no backticked noun.verb after ### 8.1); only this repo's own lint on the real FRAMEWORK (48 names, incl. noun.verb) catches it

- **affects:** engine maintainers editing guards.py::spec_items
- **why not eliminated:** a unit-level pin needs a fixture with a noun.verb after ### 8.1, not yet written
- **control:** collective: gate lint of this repo's records against the real FRAMEWORK (G-D12)
- **from:** CE-164, session 2026-11-07e

## INV-217: INV-86's new title understates the residual: the gate_receipt regex \bgate\b[^;,.]*?\bnot run\b also accepts a not run that is not said of the gate when it follows the word gate in the same clause ('gate green but lint not run', 'Gate status: lint not run' both pass with no gate result); reword INV-86 to 'a not run after the word gate in the same clause'

- **affects:** a session closing with a guards receipt
- **why not eliminated:** a regex cannot tell whose not run it is without parsing the sentence; the clause bound was chosen as good enough
- **control:** individual: the gate_receipt pattern in context.toml and the refusal remedy text
- **from:** CE-165, session 2026-11-07e

## INV-218: kit manual-mode.md (session close step 2) and cli.py's --guards help still say 'or that it was not run and why' / 'or not run' without saying the not run must open the receipt or be said of the gate

- **affects:** a writer following the runbook or --help rather than the refusal
- **why not eliminated:** the plan left them as they are, trusting the refusal's remedy to guide the writer
- **control:** individual: the refusal remedy text of the guards-receipt check
- **from:** CE-165, session 2026-11-07e

## INV-219: DEC-288 narrows the literal 'whole receipt is not run' reading that DEC-162 (itself PROVISIONAL, actor 'owner asked') took over; the owner has not reviewed it

- **affects:** the owner
- **why not eliminated:** an agent's call stays PROVISIONAL until the owner reviews it
- **control:** individual: decision accept after owner review (DEC-288 PROVISIONAL status)
- **from:** CE-165, session 2026-11-07e

## INV-220: working.py::Engine._followable's fallback remedy for an unknown kind (f"{verb} a closed session only") is unpinned by any test

- **affects:** a future maintainer adding a followable kind
- **why not eliminated:** no other kind exists today so the branch is unreachable
- **control:** individual: none beyond review; pin it when a new kind is added
- **from:** CE-165, session 2026-11-07e

## INV-221: doc_freeze's with self.store.lock() gap is still unpinned (removing the lock leaves the suite green)

- **affects:** concurrent sessions freezing docs
- **why not eliminated:** out of CE-165's scope; the builder flagged it
- **control:** individual: none yet; a lock-presence test like criterion_new's would pin it
- **from:** CE-165, session 2026-11-07e

## INV-222: commit.py::_commit timeout-after-commit branch (_reset with partial else paths) is untested when grafts are present

- **affects:** a session whose banner commit times out
- **why not eliminated:** the branch is reached only by a timeout after the commit lands, hard to provoke in a test
- **control:** individual: review only; the CE-125 partial-path test covers the non-graft case
- **from:** CE-175, session 2026-11-07e

## INV-223: _reset of HANDOFF.md after a graft commit drops another session's staged HANDOFF content from the real index (the working file is kept)

- **affects:** a concurrent session that had staged HANDOFF.md
- **why not eliminated:** matches the CE-125 partial path, which does the same for other paths; staging by another session is rare
- **control:** individual: commit by path and never stage in a shared tree (CLAUDE.md rule)
- **from:** CE-175, session 2026-11-07e

## INV-224: the graft blob mode is hardcoded to 100644, as the op log's is

- **affects:** a repo whose HANDOFF.md has another mode
- **why not eliminated:** HANDOFF.md is never executable or a symlink in practice
- **control:** individual: none beyond review
- **from:** CE-175, session 2026-11-07e

## INV-225: working.py::Engine._lint_carried still lints the whole working note, so a broken hand edit can refuse a banner-only commit

- **affects:** a session setting a banner while another session's hand edit to HANDOFF.md is broken
- **why not eliminated:** out of CE-175 scope; the builder flagged it
- **control:** individual: the refusal names the lint failure; fix the hand edit or revert it
- **from:** CE-175, session 2026-11-07e

## INV-226: the by-hand runbook step for the graft when no op lines are left assumes the reader switches from git commit --only to the temporary-index flow, implied but not spelled out

- **affects:** a writer committing a banner by hand
- **why not eliminated:** the step was written for the case with op lines left
- **control:** individual: the manual-mode row Commit the write and commit.py::_commit_partial as the reference
- **from:** CE-175, session 2026-11-07e

## INV-227: An undeclared CE_GATE_PART makes the scope guard fall back to require and its verdict wrongly says 'no CE_GATE_PART'

- **affects:** an adopter reading the guard message
- **why not eliminated:** wording only, the fallback verdict is still correct
- **control:** individual: the guard still refuses on the fallback scope
- **from:** CE-181, session 2026-11-07e

## INV-228: A test inside a part that runs pytest directly in a nested temp repo inherits CE_GATE_PART

- **affects:** engine test authors
- **why not eliminated:** matters only if the nested repo declares a part with the same name
- **control:** individual: none beyond the naming convention
- **from:** CE-181, session 2026-11-07e

## INV-229: Pytest parts need __pycache__ gitignored or a run comes back INCONSISTENT; undocumented for adopters (true of single-command pytest gates too)

- **affects:** adopters with pytest gates
- **why not eliminated:** documentation gap, not engine behaviour
- **control:** individual: gate INCONSISTENT verdict names the drift
- **from:** CE-181, session 2026-11-07e

## INV-230: Kit gate.md row 'Exclude only what no test reads but the readers' reads oddly under parts, which take no readers; the added parenthetical does not fully fix it

- **affects:** adopters reading the kit runbook
- **why not eliminated:** wording only
- **control:** individual: the kit gate.md parenthetical
- **from:** CE-181, session 2026-11-07e

## INV-231: Whole-gate result relies on the recorded run (1988 passed, 783.9s) and gate status --require code rc 0 on g1/code:fd26c56ee3da9623 at HEAD, not a fresh full re-run

- **affects:** the owner at push time
- **why not eliminated:** verifier did not re-run the full 13-minute gate
- **control:** individual: gate status --require code and the pre-push full gate
- **from:** CE-181, session 2026-11-07e

## INV-232: The prompt in .claude/agents/housekeeper.md writes the tier-1 line as `<short sha> <id>: tier 1: ...` but hk_run prints it with a `  - not done: ` prefix; a model should still match it

- **affects:** the housekeeper agent
- **why not eliminated:** matching is left to the model, not code
- **control:** individual: the first live housekeeper run confirms the match
- **from:** CE-12, session 2026-11-07e

## INV-233: Engine-made commits whose title names an open task (e.g. fb1a908 `engine: new DEC-302, promote CE-12`) produce tier-1 lines the agent must skip every session

- **affects:** the housekeeper agent token cost
- **why not eliminated:** the scan lists any title mention, engine commits included
- **control:** individual: the agent prompt tells it to skip them; a scan filter on engine: titles would reduce it
- **from:** CE-12, session 2026-11-07e

## INV-234: No test pins that a --text citing a different commit hash still gets the sha prefix (code tests prefix-of-full-hash, not any-hash-present)

- **affects:** future edits to hk_comment
- **why not eliminated:** behaviour is correct but unpinned
- **control:** individual: the existing scan tests cover the cited-own-hash cases only
- **from:** CE-12, session 2026-11-07e

## INV-235: The housekeeper agent has never run against a live MCP server (server is stale), so the hk_ tool names resolving is unconfirmed

- **affects:** the housekeeper agent
- **why not eliminated:** MCP server restart needed
- **control:** individual: test_this_repos_housekeeping_agent_names_only_hk_tools checks names against the tool registry; first live run confirms
- **from:** CE-12, session 2026-11-07e

## INV-236: DEC-302..306 are PROVISIONAL and await the owner review

- **affects:** the owner
- **why not eliminated:** agent calls stay PROVISIONAL until the owner reviews them
- **control:** individual: context-engine decision accept after owner review
- **from:** CE-12, session 2026-11-07e

## INV-237: The §3.3 rule (an open board item for every manual criterion) is not enforced until CE-206 is built; the repo has 0 manual criteria today

- **affects:** agents writing manual criteria before CE-206
- **why not eliminated:** enforcement is a lint and refusal that is its own task
- **control:** individual: CE-206 (manual-criterion lint and refusal)
- **from:** CE-194, session 2026-11-07e

## INV-238: CE-194's title still says 'beside P7' while P19 went at the end of §1

- **affects:** a reader trusting the title's placement
- **why not eliminated:** record titles are not edited after the fact
- **control:** individual: DEC-307 records why P19 went at the end of §1
- **from:** CE-194, session 2026-11-07e

## INV-239: Only the code gate scope was green at verification; all and code+readers have no recorded run on the current content id

- **affects:** the next pusher
- **why not eliminated:** record commits followed the gate run
- **control:** collective: every push runs the whole gate plus tools/linux_gate.py
- **from:** CE-194, session 2026-11-07e
