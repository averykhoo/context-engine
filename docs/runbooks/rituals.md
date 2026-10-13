---
type: Runbook
title: "Rituals: every ritual's steps in order, the engine command and the by-hand step side by side"
source: FRAMEWORK §6, P16
created: 2026-10-12
---

# Rituals

The **order** of each ritual lives here and nowhere else. FRAMEWORK §6 says what each ritual must
achieve, its guards and its reasons; this file says what to do, in what order. Each step gives:

- **§**: its item number in that FRAMEWORK §6 subsection (`—` if it has none). These numbers are
  stable (P3): records cite them, and they are labels, not the order. The order is the order of
  the rows.
- **Engine**: the `context-engine` command (`<engine-python> -m context_engine ...`, with
  `CE_ACTOR` and `CE_SESSION` set). Over MCP the same operation is the tool
  `mcp__context-engine__<group>_<verb>` (`init` is `mcp__context-engine__init`, `why` is
  `mcp__context-engine__why`), except `baton expire`, which is
  `mcp__context-engine__hk_expire_batons`, and `decision index`, which is
  `mcp__context-engine__hk_regen_index`. `—` means the step is not an engine operation.
- **By hand**: the same step without the engine, as a link into
  [manual-mode.md](manual-mode.md), which does every operation by hand and says why.
- **Why**: what the step protects, so a session whose engine erred knows what the right result
  was.

When the engine errors, or refuses what it should allow, do that step by hand and fix the engine
([manual-mode § When the engine and this runbook disagree](manual-mode.md#when-the-engine-and-this-runbook-disagree)).
A refusal with a sensible remedy is not an error: follow the remedy. `<gate>` below is the repo's
gate: its own test command, then `context-engine lint`, as its contract states.

## Where each part of FRAMEWORK §6 is done

| FRAMEWORK | Steps |
|---|---|
| §6.1 Session start | § Session start; § Resume |
| §6.2 Intake | § Intake |
| §6.3 Clean close | § Clean close |
| §6.4 Pause | § Pause; § Resume |
| §6.5 Decision recording | § Intake (a decision is recorded there, with its actor) |
| §6.6 Delegation and build rounds | no steps: a method, not a ritual; its rules are FRAMEWORK §6.6 |
| §6.7 Promotion and demotion | § Clean close (item 5) and § Housekeeping (expiry) |
| §6.8 Push and CI | § Push and CI |
| §6.9 Bootstrap | § Bootstrap |
| §6.10 Humans working outside the rituals | § Foreign reconcile |
| §6.11 Housekeeping | § Housekeeping |
| §6.12 Keeping this document current | § Clean close (item 5) |
| §6.13 Rollback and close | not designed yet: no steps |

## Session start (§6.1)

Orientation in one bounded read, carried work first. Do not re-rank the board now; that is
clean close's job (FRAMEWORK §5.2).

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| 1 | The contract is loaded: global, repo (`CLAUDE.md`, `AGENTS.md`, and the framework contract `CLAUDE.md` imports) and subtree; in an adopted repo the `SessionStart` hook has put `orient`'s output in the context | — | read them if the harness did not; if no orient output is there, the hook did not run (it fails silently): run `orient` yourself after the next step and tell the owner | the rules come before the work |
| — | Mint the session key and reserve it with a `kind: open` stub; use the key as `CE_SESSION` | `context-engine session start` | [§ session start](manual-mode.md#context-engine-session-start) | two sessions never share a key, and a live session is visible to the others (§5.5) |
| — | Start-of-session housekeeping: stale stubs, foreign commits, hand-written receipts | — | § Housekeeping, at session start | what happened since the last session is reconciled before it is built on |
| 2–5 | Read the banner, open batons and pauses (yours first), other open sessions, the NEXT tier, the questions to raise, and the top item's brief, Traps and Read first | `context-engine orient` | [§ orient](manual-mode.md#context-engine-orient) | one capped read replaces opening a dozen files |
| — | Show the owner the other open sessions it lists, in chat, one line each: the key, when it opened and its newest commit; say "none" when there are none. Stop, close or abandon none of them without the owner's word | `context-engine orient` (its open-sessions section); `git log -1 --format='%h %cr' --grep='Session: <key>'` per key | [§ orient](manual-mode.md#context-engine-orient) item 3 | an open stub is either a live session in another window or one that died; only the owner knows which, and what to stop |
| 2 | Do the open batons and pause records it lists before anything else: finish each baton, resume each pause | `context-engine baton done`; § Resume | [§ baton done](manual-mode.md#context-engine-baton-done); § Resume | carried work is the most urgent and the easiest to lose |
| 3 | Raise every question it lists (NEXT tier and overdue) in chat, one line each, with any flags from background checks; then stamp them | `context-engine ask raised <ids>` | [§ ask raised](manual-mode.md#context-engine-ask-raised) | the stamp restarts the overdue clock, and the stub line is the receipt the close checks (G-W8) |
| 4 | Show the top item, or the one the owner assigned (an assignment overrides the ranking) | `context-engine task show <id>` | [§ task show](manual-mode.md#context-engine-task-show) | the item is the unit of work; its body says how to start |
| 5 | Read that item's `## Read first` list | — | open each file it names | the item's author knew what is needed to start |
| 6 | Read the rest of the note only if needed; remember what you read for the close's `read:` receipt | — | open `HANDOFF.md` | the receipt measures how cheap orientation is |

Background check agents (FRAMEWORK §6.1, tier 1 and 2) are optional. A repo that runs them fires
them right after session start; they report only, and the session triages their flags in step 3.

## Resume (§6.1, §6.4)

When `orient` lists an open pause record of your own session's line of work, or the owner says
"continue".

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| — | Read the pause record: what was in flight, the resume step, the branch, the uncommitted paths and the deferred steps | `context-engine orient` | [§ orient](manual-mode.md#context-engine-orient); open the record in the pause directory | the record, not memory, is the state to resume from |
| — | Re-check the tree against it: the branch (`git rev-parse --abbrev-ref HEAD`) and the uncommitted paths (`git status --porcelain=v1 --untracked-files=all`); explain every difference before going on | — | git | another session may have committed, moved or lost those paths since |
| — | Do the resume step, then the deferred steps (gate, commit of the work, re-ranking, banner, runbook filing) | — | as each step's own section says | a pause defers these; it never drops them (FRAMEWORK §6.4) |
| — | Mark the record resumed | `context-engine pause resume <id>` | [§ pause resume](manual-mode.md#context-engine-pause-resume) | `orient` stops listing it, and the record says who picked it up |

## Intake (§6.2)

The owner gives intent. Record it before acting on it.

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| 1 | Record the words **verbatim, now**: behaviour-shaped as a new story or an amendment; choice-shaped as a decision with `actor: owner`, or a charter edit; an answer to an open question through `ask answer`. Write the words to a file with an editor, not a shell heredoc. Tell the owner in one line which it became | `context-engine record new story "<title>" --file <words.md> --set actor=owner ...`; `context-engine record amend <id> "<words>"`; `context-engine record new decision ...`; `context-engine ask answer <id> "<words>" --title "<title>"` | [§ record new](manual-mode.md#context-engine-record-new); [§ record amend](manual-mode.md#context-engine-record-amend); [§ ask answer](manual-mode.md#context-engine-ask-answer) | owner words exist only in one transcript until recorded; a stamped record cannot drift (G-D10); heredocs can mangle quotes and backslashes |
| 2 | Link it to the charter goals (`goals: [G-n, ...]` on a story); if none fits, ask: it may be a new goal | `context-engine record new story ... --set goals=[G-n]` | [§ record new](manual-mode.md#context-engine-record-new) | every story traces to a goal, or the charter is missing one |
| 3 | Draft the criteria, live by default; show the owner a digest of three to seven lines, never files. A story marked `sign-off: required` keeps them `planned` until the owner stamps them | — | edit the criteria file | the owner sees what "correct" will mean before it is built |
| 4 | Every owner-only uncertainty becomes a question on the board, with a recommendation held with reasonable confidence where one is cheap to reach (FRAMEWORK §5.3); raise it in chat this session | `context-engine ask new "<question>"`; `context-engine ask raised <ids>` | [§ ask new](manual-mode.md#context-engine-ask-new); [§ ask raised](manual-mode.md#context-engine-ask-raised) | never guess at what only the owner can decide (P8) |
| 5 | If it contradicts an existing decision or criterion, say so at once, and record the outcome as a decision that supersedes or amends the old one | `context-engine record new decision ...`, then `context-engine decision supersede <old> <new>`; `context-engine record amend <id> "<text>"` | [§ record new](manual-mode.md#context-engine-record-new); [§ decision supersede](manual-mode.md#context-engine-decision-supersede); [§ record amend](manual-mode.md#context-engine-record-amend) | a silent contradiction is drift nobody chose |
| 6 | On a design change, run a criteria census (each criterion in scope: KEEP, rewrite or retire, with the work assigned) and keep it as an evidence doc | — | write the evidence doc | criteria staled by a design change are found together, not one red at a time |

An agent's own decision of consequence is recorded the same way, with its own actor from the
FRAMEWORK §6.5 vocabulary (`agent (<model-id>)`, `owner asked`, ...). Never `actor: owner` on the
agent's own call.

## Clean close (§6.3)

A natural stopping point. **Close by default when the work you were asked for is done**, without
waiting to be told; stay open only when the owner says so, and pause (§ Pause) at an awkward stop.
More work asked for after the close starts a new session (§ Session start). The records come
first, then the gate, then the ledger entry that carries the gate's result, then the commit.

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| 0 | Every owner word given this session is recorded | as § Intake, step 1 | § Intake | the most easily lost thing of all |
| 1 | Lint, to see what earlier sessions left red, before adding to it | `context-engine lint` | [§ lint](manual-mode.md#context-engine-lint) | a red you did not cause must not be mistaken for one you did, or hidden under yours |
| 4 | The board: close what is done (a reviewed item files its residuals in the register), comment on what moved, re-rank, file new items; rewrite the summary, `## Traps` and `## Read first` of every NOW and NEXT item you touched | `context-engine task close <id> -m "<message>"`; `context-engine task comment`; `context-engine task touch`; `context-engine task promote <id> <tier>`; `context-engine task new`; `context-engine task section` | [§ task close](manual-mode.md#context-engine-task-close); [§ task comment](manual-mode.md#context-engine-task-comment); [§ task touch](manual-mode.md#context-engine-task-touch); [§ task promote](manual-mode.md#context-engine-task-promote); [§ task new](manual-mode.md#context-engine-task-new); [§ task section](manual-mode.md#context-engine-task-section) | the board is what the next session reads first; the ledger's `rows:` names these items, so they come before it |
| 6 | Anything skipped becomes a baton | `context-engine baton add "<step>" --why "<why>"` | [§ baton add](manual-mode.md#context-engine-baton-add) | a sentence in a banner the next close overwrites is lost; a record is not (§5.4) |
| 5 | Durable rules go into the contract; method lessons into a runbook; a change to how the framework works goes into FRAMEWORK.md in place | — | edit the files | a lesson left in a transcript is relearned (§6.7, §6.12) |
| 6a | Pre-close housekeeping: carry out what this session recorded but did not finish | `context-engine baton expire` (MCP: `hk_expire_batons`); `context-engine record stamp` | [§ baton expire](manual-mode.md#context-engine-baton-expire); [§ record stamp](manual-mode.md#context-engine-record-stamp); the rest of § Housekeeping, before close | recorded intent that is not carried out is forgotten; its operation list goes into the digest |
| 2 | Run `<gate>`; then write the ledger entry over your stub: `rows` (the items touched), the summary (the digest, at most 7 lines), the receipts (`guards` = the gate result verbatim, `read`, `asked`) and `Still owed` | `context-engine session close --rows ... --summary ... --guards ... --read ... --asked ... --owed ...` | [§ session close](manual-mode.md#context-engine-session-close) | the close is what the next session trusts; it refuses a receipt that misses an open question (G-W6, G-W8) |
| 3 | Replace the banner: read it and keep its hash, then write yours with that hash; if refused, another session wrote it: read theirs, merge, retry | `context-engine banner show`; `context-engine banner set --seen <hash> --file <banner.md>` | [§ banner show](manual-mode.md#context-engine-banner-show); [§ banner set](manual-mode.md#context-engine-banner-set) | the banner is the one paragraph every session reads; it must never silently erase another session's truth (§5.5) |
| 7 | Lint and `<gate>` again, then commit by path (`git commit -o <paths>`, never the whole tree, never `git stash`), each commit with a `Session: <key>` trailer; push only with permission (§ Push and CI) | `context-engine lint` | [§ lint](manual-mode.md#context-engine-lint) | the second run proves this close; committing by path never sweeps up another session's work |
| 8 | The owner digest in chat, at most 7 lines | — | — | inform-and-proceed only works if the owner sees what was decided (§5.6) |

## Pause (§6.4)

An awkward stopping point; the work continues next session. Only the cheap, unrecoverable steps
are mandatory.

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| 0 | Every owner word given this session is recorded | as § Intake, step 1 | § Intake | they exist only in this session's transcript |
| 1 | Evidence out of scratch, into a tracked doc (rough, dated and ACTIVE-PLAN is fine) | — | write the doc | scratch is ignored by git, so anything only there is already lost |
| 3 | The pause record: what is in flight, the resume step, the branch, every uncommitted path and the deferred steps; committed by path at once | `context-engine pause open --in-flight "<what>" --resume "<first step>" --deferred "<steps>"` | [§ pause open](manual-mode.md#context-engine-pause-open) | the next session resumes from the tree's real state, and a committed record cannot be swept away by another session's close |
| 2 | The ledger entry, `kind: pause`: rows and deferred steps | `context-engine session pause --rows ... --deferred ...` | [§ session pause](manual-mode.md#context-engine-session-pause) | one ledger entry per session without exception; too many pauses in a row fail G-W2 |
| — | Commit the ledger and op log by path | — | `git commit -o <paths>` with a `Session: <key>` trailer | the entry is the evidence the session existed |

Deferred, not dropped: the gate, the commit of the work itself, re-ranking, the banner and
runbook filing. The next session does them (§ Resume).

## Push and CI (§6.8)

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| — | Ask the owner; push only with permission. A push hold, if any, is a line at the top of the contract | — | — | a push reaches other people; it is the owner's call |
| — | `<gate>` green on exactly the commit being pushed | `context-engine lint` | [§ lint](manual-mode.md#context-engine-lint) and the test command | never push red or unverified |
| — | Push, and note the pushed commit's hash (`git rev-parse HEAD`) | — | `git push` | the watcher finds runs by hash, not "the latest run", which may be another session's |
| — | Start a background CI watcher: it finds the runs for that hash (allowing about a minute for them to appear), waits for them to finish, and reports a verdict per run, with the failing step and the log lines around the first error for each failure. It writes its report to a file as it goes. It only watches: no fix, no re-run, no cancel, no push | — | the harness's background agent, or the CI web page | a re-run hides a flaky failure; a fix is the session's job, with the gate |
| — | Without CI (the repo has no workflow, or CI cannot run): do CI's run by hand. The contract's gate names the CI workflow file, if there is one | — | in a fresh environment at the declared Python floor (`requires-python`), clone or check out exactly the pushed commit, install the package with its dev extra only (`pip install -e ".[dev]"`), then `<gate>` | a fresh environment catches what a working one hides: a dependency that was installed by hand and never declared |
| — | Report the verdict to the owner. The push is not done until the watcher reports, and a red run is never described as done | — | — | a push nobody watched is unverified |

## Bootstrap (§6.9)

A repo gets the framework. The engine's adoption kit (`kit/` in the installed package, and its
`README.md`) holds every file and the install, pin and upgrade steps.

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| 1 | The owner gives, in chat, a charter (about a page), the first stories and any mandates | — | — | the charter is the root of the correctness chain |
| 2 | Install the engine into its own environment, pinned to a release tag or commit, never into the repo's environment; register the MCP server only if the repo wants it | — | the kit README § 1 | the repo never imports the engine, so the engine cannot break the repo's own environment |
| 3 | Write the kit into the repo: the layout, `context.toml`, the skeletons, these runbooks, the bootloader appended to `CLAUDE.md`, the framework contract it imports, and the `SessionStart` hook in the machine-local settings. Nothing existing is overwritten | `context-engine init` | [§ init](manual-mode.md#context-engine-init) | every file the rituals expect exists from the first session, and an existing repo loses nothing |
| 3 | Fill the charter (goals get `G-n` ids) and the config, with a provenance note on every cap; set `[guards]` `charter`, `stories` and `tests` so the intent-chain guards run; check the id prefixes against ids the repo already uses; put the real test command into `CLAUDE.md` § Gate | — | edit `docs/charter.md`, `context.toml`, `CLAUDE.md` | a cap with no provenance cannot be revisited; a colliding prefix makes two things share an id |
| — | Lint is green, then open the first session | `context-engine lint`; `context-engine session start` | [§ lint](manual-mode.md#context-engine-lint); [§ session start](manual-mode.md#context-engine-session-start) | the first session starts from a clean record |
| 1 | Record the owner's charter words and first stories | as § Intake, step 1 | § Intake | the first stories are owner words like any other |
| 4 | Draft the criteria and show a digest; open the owner questions; build the first board | `context-engine ask new`; `context-engine task new` | [§ ask new](manual-mode.md#context-engine-ask-new); [§ task new](manual-mode.md#context-engine-task-new) | the first board ranks the work the charter implies |
| 5 | The first clean close (§ Clean close): the gate is green, the ledger entry is `kind: close`, and the first banner is written with `--seen none` | `context-engine session close ...`; `context-engine banner show`; `context-engine banner set --seen none --file <banner.md>` | [§ session close](manual-mode.md#context-engine-session-close); [§ banner show](manual-mode.md#context-engine-banner-show); [§ banner set](manual-mode.md#context-engine-banner-set) | `none` is the hash of "no banner yet", so the first write is as safe as every later one |

## Foreign reconcile (§6.10)

At session start, for commits made outside the rituals since the newest ledger entry. Humans are
never required to perform rituals: the next agent session absorbs the cost.

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| 2 | Find the foreign commits: those after the last commit that touched the ledger and carrying no `Session:` trailer | — | `git log --format='%h %an %s [%(trailers:key=Session,valueonly,separator=%x2C)]' <sha>..HEAD`, where `<sha>` is `git log -1 --format=%H -- <ledger>`; foreign ones show `[]` | an agent commit always carries the trailer (item 1), so a commit without one was made by hand |
| 2 | Write a ledger entry for them: mint the next key as session start does, and insert `## <key> · kind: foreign` at the top, with `- **commits:** <short sha> <author>: <what changed>; ...` and `- **reconciled by:** <your key>` | — | [§ session start](manual-mode.md#context-engine-session-start) for the key and the entry layout | the ledger has an entry for every change to the repo, so a human's work is visible to the next session |
| 2 | Trace-check them: criteria, prose or board items they may have staled become a task or a comment | `context-engine task new`; `context-engine task comment <id> "<text>"` | [§ task new](manual-mode.md#context-engine-task-new); [§ task comment](manual-mode.md#context-engine-task-comment) | a hand edit that changes behaviour stales the text describing it |
| 2 | Inbox-check them for intent: a commit message or doc edit that states a feature or decision is recorded as a story or decision, `via: commit <sha>`, with the author as its actor (`human:<id>`) | `context-engine record new ...` | [§ record new](manual-mode.md#context-engine-record-new) | intent is recorded wherever it was stated, attributed to whoever stated it |
| 4 | A human commit that turned a guard red is not reverted: fix or reconcile it, and say so in the close's summary | `context-engine lint` | [§ lint](manual-mode.md#context-engine-lint) | a human's red guard is the agent's job |

## Housekeeping (§6.11)

The repair pass for things that should happen and keep being forgotten. It **carries out intent
already recorded somewhere and never forms new intent**. Without housekeeping agents (or without
the engine), the main session does all of it, by tier-0 rules: every write is marked
`"mechanical": true` in the op log, with actor `process:housekeep` (or the session's own), and is
committed by path with a `Session: <key>` trailer, so `git revert` undoes it. The operation list
goes into the owner digest.

**At session start** (reconcile what happened since the last session):

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| — | A stale `kind: open` stub (another session's, older than the window the contract names; with none named, one with 2 or more closes or pauses after it) becomes `kind: abandoned`: change the kind in its heading, keep its lines, add `- **abandoned:** <your key>: never closed or paused`, and file a baton for whatever it left in flight | `context-engine baton add "<step>" --why "<why>"` (the ledger edit is not an operation yet) | [§ session start](manual-mode.md#context-engine-session-start) for the entry layout; [§ baton add](manual-mode.md#context-engine-baton-add) | a dead session must not look live, and its unfinished work must reach someone (G-W11) |
| — | Foreign commits | — | § Foreign reconcile | a human's work enters the record |
| — | A close whose `asked:` receipt was written by hand (no `ask.raised` op line for it): set `last_asked` to that session's key on each question it names | — (not an operation yet) | [§ ask raised](manual-mode.md#context-engine-ask-raised) for the keys written | the overdue clock must restart when a question really was raised |
| — | Commits since the last session that name a board item in their title: a dated comment on the item | `context-engine task comment --mechanical <id> "<sha>: <subject>"` | [§ task comment](manual-mode.md#context-engine-task-comment) | the item's log shows its history without reading git |
| — | A pause record whose uncommitted paths are all committed now: mark it resumed, citing the commit | `context-engine pause resume <id>` | [§ pause resume](manual-mode.md#context-engine-pause-resume) | a pause whose work landed is not carried work any more |

**Before close** (§6.3 item 6a: carry out what this session recorded but did not finish):

| § | Do | Engine | By hand | Why |
|---|---|---|---|---|
| — | Expire every baton and pause with 2 or more closes or pauses after its session into a LATER task | `context-engine baton expire` (MCP: `hk_expire_batons`) | [§ baton expire](manual-mode.md#context-engine-baton-expire) | carried work must not drift for ever (G-W3) |
| — | Close each item named by a `Closes: <id>` trailer in a commit, citing the commit; anything else housekeeping would close is proposed to the session, never closed by it | `context-engine task close <id> -m "done in <sha> (Closes: trailer)"` | [§ task close](manual-mode.md#context-engine-task-close) | a close needs evidence; a mechanical close without it is someone quietly declining to record a judgement |
| — | Stamp every append-only record whose body is final | `context-engine record stamp <ids>` | [§ record stamp](manual-mode.md#context-engine-record-stamp) | an unstamped owner's words can still drift (G-D10) |
| — | Mark items housekeeping updated without progress | `context-engine task touch --mechanical <id>` | [§ task touch](manual-mode.md#context-engine-task-touch) | a mechanical touch must not look like progress |
| — | Regenerate the decision index, where `[working] decision_index` is set (every engine write to a decision already does; a by-hand decision does not) | `context-engine decision index` (MCP: `hk_regen_index`) | [§ decision index](manual-mode.md#context-engine-decision-index) | a generated file is checked by byte equality, so a stale one is red (G-D6) |
| — | Raise floor ratchets and regenerate any other generated file, where the repo has them, as the guard that names each one says | — | regenerate or raise by hand | as above |
