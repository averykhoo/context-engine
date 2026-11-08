# Global CLAUDE.md audit: which rules the framework already holds (CE-40)

ACTIVE-PLAN while CE-40 is open; freeze it when CE-40 closes.

Session 2026-11-07e, claude-code/claude-opus-5-5, 2026-11-08. Audited: the owner's global
`~/.claude/CLAUDE.md`, sha256 `7294a14c73f63a940a0087d34eea2c335cae2b8d9b78d5904cb72510d78b0fb9`, 411 lines, read 2026-11-08. Checked against HEAD
`a67df78`: `docs/framework/FRAMEWORK.md`, `docs/framework/contract.md` and `docs/runbooks/*.md`.
Owner words: the item's brief (2026-10-13a), and DEC-162, which accepts the gap (repos without
the framework lose what moves out). This doc proposes; the owner pastes § 4 by hand. Nothing here
edits the global file. Agent calls: DEC-317 to DEC-321 (PROVISIONAL).

## 1. Verdict per rule

One row per rule of the global file, grouped by its sections. A rule with two covering lines gets two rows with the
same id. Verdicts:

- **COVERED**: the framework holds it; the quote is the covering line.
- **DIVERGES**: the framework holds the topic but says something else; the quote is the framework's line (§ 2).
- **GAP**: framework-shaped, but no framework text holds it; the quote cell lists terms with 0 hits in
  `docs/framework/FRAMEWORK.md`, `docs/framework/contract.md` and `docs/runbooks/*.md` at HEAD (§ 3).
- **MACHINE**: a fact about this laptop, its tools or the owner's other repos; stays global.
- **HARNESS**: a fact about Claude Code itself; stays global.
- **DROP**: provenance (a dated incident or measurement) that justifies a rule but is not one.

A quote is a verbatim substring of `git show HEAD:<file>` once every run of whitespace is collapsed to one space;
the § 5 checker confirms each one. Files are cited by § heading, never by line number.

### Header

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R1 | Repo-specific rules live in each repo's CLAUDE.md and win where they conflict | MACHINE | - | - (kept; § 4 adds the framework pointer under it) |

### Two shells: do not mix their syntax

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R2 | the shell-syntax table, the here-string trap, suspect the Bash direction first | MACHINE | - | - |
| R3 | execution policy is Restricted; how to run a .ps1 with Bypass | MACHINE | - | - |
| R4 | `6>$null` suppresses a Write-Host banner | MACHINE | - | - |

### Python environments

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R5 | bare python is a Store stub; conda and uv not on PATH; pixi is; the conda.exe path | MACHINE | - | - |
| R6 | one env per repo folder, lowercase; call its interpreter by full path; conda run forwards no stdin | MACHINE | - | - |
| R7 | if the env does not exist, ask before creating it | MACHINE | - | - |
| R8 | the known deviations (SpeechEnhancement, audio-workspace, gitlab-admin-scripts) | MACHINE | - | - |

### Docker

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R9 | Engine in WSL, never Docker Desktop, the guard shim and its refused verbs, no sudo, Linux filesystem, the WSL memory cap | MACHINE | - | - |
| R10 | turn it off: a session that starts a long-lived process owns stopping it; name what is left up; ask before `wsl --shutdown` | MACHINE | docs/runbooks/release.md § The fresh-user install trial | remove the environment, confirm it is gone, delete the temp directory, and leave nothing running. |

R10's only framework echo is the install trial's clean-up; the general "own what you start" rule is a GAP candidate
(§ 3), and its Docker form stays global.

### Concurrent sessions: the working tree is shared

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R11 | several sessions per repo; the start-of-session status goes stale; re-run git status before editing or committing | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P12 | Commit by path; never `git stash` in a shared tree; re-check `git status` right before committing. |
| R11 | (same) | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P12 | Another session's commit can absorb uncommitted files, or land minutes before yours. |
| R12 | HANDOFF.md and the decision log are the collision points; write up last; ask before restructuring | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P12 | working-state files must be safe with several writers |
| R13 | commit by path; never `git add -A`; never `git stash` | COVERED | docs/framework/contract.md § Rules | never `git add -A`, never `git stash`: sessions may share the working tree. |
| R14 | subagent transcripts under `subagents/workflows/<runId>/` record every Write and Edit | HARNESS | - | - |
| R15 | the dated incidents (2026-07-28, 2026-10-07 and its commit) | DROP | - | - |

### .scratch/

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R16 | throwaway; anything only there is already lost; evidence to a tracked file the same hour | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P10 | `.scratch/` is throwaway space: anything recorded only there is already lost. |
| R16 | (same) | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P9 | evidence still in scratch; |
| R16 | (same) | COVERED | docs/runbooks/procedures.md § Pause (§6.4) | Move evidence out of `.scratch/` into a tracked doc |
| R17 | SpeechEnhancement and skillscape have no .scratch/ or ignore entry; gitlab-admin-scripts' git history; check a file is tracked | MACHINE | - | - |
| R18 | a sweep is audited by a read-only agent; the agent audits, the session deletes | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P11 | The audit-only rule stands for anything that cannot be undone, such as deleting from `.scratch/`. |
| R18 | (same) | COVERED | docs/framework/FRAMEWORK.md § 6.6 Delegation and build rounds | an agent that reads `.scratch/` and deletes nothing (P11) |
| R18 | (same) | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | Agents audit; the session decides and deletes. |
| R19 | the four classes DERIVABLE, SUPERSEDED (name the file, quote the line), SALVAGE, UNCLEAR; SALVAGE is the deliverable | GAP | - | absent: SALVAGE |
| R20 | exclude the auditing agent's own report directory from the sweep | GAP | - | absent: report directory, own report |
| R21 | bulk deletes go to the Recycle Bin, not `rm -rf` | MACHINE | - | absent: Recycle |
| R22 | transcribe every SALVAGE into a tracked file before deleting, same session | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | the session deletes the run's scratch files once their conclusions are in tracked files (P10), in the same session. |
| R23 | the 2026-09-20 size measurement and the fixture anecdote | DROP | - | - |

R19's nearest framework line is the roster's sweep-auditor row, "a class per entry, naming the tracked file each
finding worth keeping belongs in (P10)": it asks for classes but names none of the four.

### HANDOFF.md (when a repo has one)

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R24 | read it at session start, in full, right after CLAUDE.md | DIVERGES | docs/runbooks/procedures.md § Session start (§6.1) | Read the rest of the orientation note (`HANDOFF.md`) only if needed |
| R25 | a task the user assigns overrides its ranking | COVERED | docs/runbooks/procedures.md § Session start (§6.1) | an assignment overrides the ranking |
| R26 | CLAUDE.md is durable, HANDOFF.md volatile; finished work moves to a dated log; promote durable rules | COVERED | docs/framework/FRAMEWORK.md § 5.1 Orientation note (`HANDOFF.md`) | No session history. |
| R26 | (same) | COVERED | docs/framework/FRAMEWORK.md § 6.7 Promotion and demotion | when it becomes a durable rule (the contract keeps a pointer) |
| R27 | write back at session end: log entry, banner, rows, closed ids, "Still owed:" | COVERED | docs/framework/FRAMEWORK.md § 6.3 Clean close (a natural stopping point) | `Still owed:`. |
| R27 | (same) | COVERED | docs/framework/contract.md § Procedures | As soon as every task the owner asked for is done, run the clean close |
| R28 | only some repos have one; do not create one unasked | MACHINE | - | - |

### Git: gate, commit, push

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R29 | committing does not need permission | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P8 | A local commit or a record write is cheap to undo |
| R30 | when the gate is green and the session changed something, commit | GAP | - | absent: commit whenever, green tree |
| R31 | pushing, MRs and PRs need permission | COVERED | docs/framework/FRAMEWORK.md § 6.8 Push and CI | push only with permission; |
| R31 | (same) | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P8 | A push, a release, a published tag, deleting untracked files, owner words and anything outside the repo are not, and stay the owner's; |
| R32 | the full gate before every push; never push red or unverified | COVERED | docs/framework/FRAMEWORK.md § 6.8 Push and CI | gate before every push; |
| R32 | (same) | COVERED | docs/runbooks/procedures.md § Push and CI (§6.8) | never push red or unverified |
| R33 | a red gate: say what is red and leave it | COVERED | docs/runbooks/gate.md § Running it | Red: say what is red and leave it. Never commit on a red gate to make progress look verified |
| R34 | keep CI/CD config changes out of feature branches unless that is the task | GAP | - | absent: feature branch, CI/CD, CI config |
| R35 | every push gets a background CI watcher subagent | COVERED | docs/framework/FRAMEWORK.md § 6.8 Push and CI | the push is not done until the watcher reports; |
| R35 | (same) | COVERED | docs/runbooks/procedures.md § Push and CI (§6.8) | Start a background CI watcher on the cheapest model that can do it |
| R36 | find the runs by SHA, not the latest run; allow about a minute | COVERED | docs/runbooks/procedures.md § Push and CI (§6.8) | the watcher finds runs by hash, not "the latest run", which may be another session's |
| R36 | (same) | COVERED | docs/runbooks/procedures.md § Push and CI (§6.8) | allowing about a minute for them to appear |
| R37 | how to read CI: the gh run and GitLab pipelines/jobs commands | MACHINE | - | - (moved under § 4 CI pipelines) |
| R38 | return a verdict per run, the failing step and about 30 lines around the first error | COVERED | docs/runbooks/procedures.md § Push and CI (§6.8) | reports a verdict per run, with the failing step and the log lines around the first error |
| R39 | the watcher persists its report incrementally to `.scratch/ci-watch/<sha>.md` | COVERED | docs/runbooks/procedures.md § Push and CI (§6.8) | It writes its report to a file as it goes. |
| R40 | watch only: no fix, no re-run, no cancel, no push, no tag | COVERED | docs/runbooks/fan-out.md § Watchers | only watches: no fix, no re-run, no cancel, no push. |
| R41 | the push is not done until the verdict is in; a red run is never described as done | COVERED | docs/runbooks/procedures.md § Push and CI (§6.8) | The push is not done until the watcher reports, and a red run is never described as done |
| R42 | a release tag push is babysat through upload; confirm the version is live | COVERED | docs/runbooks/release.md § Tag, publish, confirm | have it follow the release run through its upload step |
| R42 | (same) | COVERED | docs/runbooks/release.md § Tag, publish, confirm | Confirm the version is live on the index |
| R43 | a CI watcher runs on haiku | COVERED | docs/runbooks/fan-out.md § Watchers | Use the cheapest model that can do it: haiku, or sonnet when it must read the logs. |
| R44 | every published release gets a fresh-user install trial subagent | COVERED | docs/runbooks/release.md § The fresh-user install trial | Every published release, once it is live, gets a background agent that installs the published artifact the way a stranger would. |
| R45 | a blank conda env at the declared floor (standing permission to create it); install only the version; record what pip pulled in | MACHINE | docs/runbooks/release.md § The fresh-user install trial | install `<dist>==<version>` from the index and nothing else, and record what the installer pulled in. |
| R46 | work outside the repo; confirm the package loads from the env's site-packages | COVERED | docs/runbooks/release.md § The fresh-user install trial | and confirm the package loads from that environment, not the checkout. |
| R47 | only what a user has; the quickstart verbatim, then a first hour; repo reading only to confirm, labelled | COVERED | docs/runbooks/release.md § The fresh-user install trial | Run the quickstart verbatim, then a realistic first hour |
| R47 | (same) | COVERED | docs/runbooks/release.md § The fresh-user install trial | Reading the repo is allowed only to confirm a suspected bug, and is labelled. |
| R48 | probes as files beside an incremental report | COVERED | docs/runbooks/release.md § The fresh-user install trial | kept beside a report written as it goes |
| R49 | every finding classed BROKEN (with a repro), CONFUSING / DOC GAP, or WORKS | COVERED | docs/runbooks/release.md § The fresh-user install trial | `BROKEN` (with a minimal repro), `CONFUSING / DOC GAP`, or `WORKS`. |
| R50 | clean up: remove the env, confirm it is gone, delete the temp dir, leave nothing running | COVERED | docs/runbooks/release.md § The fresh-user install trial | remove the environment, confirm it is gone, delete the temp directory, and leave nothing running. |
| R51 | the session re-runs every BROKEN repro first-hand against the source | DIVERGES | docs/runbooks/release.md § After the trial | Have a verifier agent (not the trial agent) re-run every `BROKEN` repro against the source |
| R52 | transcribe the trial into a tracked doc the same hour, and file rows | COVERED | docs/runbooks/release.md § After the trial | Put the trial in a tracked evidence doc the same hour, and file a board item for each `BROKEN` or `CONFUSING` finding |
| R53 | BROKEN is fixed and released as the next patch; a version is never reused; a pushed tag is not moved | COVERED | docs/runbooks/release.md § After the trial | Fix everything `BROKEN` and release it as the next patch version |
| R53 | (same) | COVERED | docs/runbooks/release.md § Tag, publish, confirm | A version already on the index is never reused, and a pushed tag is never moved |
| R54 | the first trial's package, version and bug count | DROP | - | - |

R45 is MACHINE for its recipe (the conda.exe line, and the standing permission to create the env, which is the one
exception to R7); its generic half is the quoted release.md line.

### CI pipelines: getting a token

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R55 | GitHub: the credential is in Credential Manager; source it per command from Bash; never print it; scopes; public repos | MACHINE | - | - |
| R56 | GitLab: the loader scripts; the PS 5.1 JSON-array traps; which repos have GitLab remotes | MACHINE | - | - |

### Delegation: subagents are for context, not parallelism

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R57 | delegate bulky reading for context, not speed; the flood test; a known lookup stays inline | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | would doing it inline flood the agent's context with file contents? |
| R57 | (same) | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | A lookup whose file and symbol are already known is done inline there. |
| R58 | ask for verdicts plus `file::symbol` evidence, never file dumps | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | the verdict form (`file::symbol` evidence, never file dumps) |
| R59 | standing permission for read-only agents of that shape | COVERED | docs/framework/contract.md § Rules | each task, even a lone one, goes to its own subagent through ultracode |
| R60 | subagent model: opus by default, sonnet bulk, haiku watcher, fable only when asked | DIVERGES | docs/framework/FRAMEWORK.md § 6.6 Delegation and build rounds | The default for delegated work is the cheapest model that can do it |
| R60 | (same) | DIVERGES | docs/framework/FRAMEWORK.md § 6.6 Delegation and build rounds | The repo's contract names the models. |
| R60 | (same; the fable half agrees) | DIVERGES | docs/framework/contract.md § Rules | Do not use `fable` subagents unless the owner asks for them or they are really necessary. |
| R61 | ultracode has standing approval when more helpful; the test is shape, not permission | COVERED | docs/framework/contract.md § Rules | needs no per-request opt-in when it keeps the session's own context and tokens down |
| R61 | (same) | COVERED | docs/framework/contract.md § Rules | one check goes to one agent, not a fan-out, and coupled work is not split up to go "faster". |
| R62 | every delegated unit persists before it returns, one file per agent, incrementally | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | each finding is appended as it lands, not buffered to the end |
| R63 | Explore cannot persist; check the file's size on return; persist on receipt | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | Only an agent that can write files can persist (not `Explore`). |
| R63 | (same) | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | check the file exists and is not short; if it is, write the returned report to it before doing anything else with it. |
| R64 | .scratch/ is the crash bag, not where findings live | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P10 | anything recorded only there is already lost. |
| R65 | the orchestrating session deletes the run's .scratch/ directory once its conclusions are tracked | COVERED | docs/runbooks/fan-out.md § Delegating reading and auditing | the session deletes the run's scratch files once their conclusions are in tracked files |
| R66 | delegation does not transfer judgement; reconcile, never average; verify first-hand | DIVERGES | docs/runbooks/fan-out.md § Delegating reading and auditing | checked by a verifier: another agent than the one that did the work |
| R66 | (same; the reconcile half agrees) | DIVERGES | docs/runbooks/fan-out.md § Delegating reading and auditing | Reports that contradict each other are reconciled, never averaged. |
| R66 | (same; the evidence half agrees) | DIVERGES | docs/runbooks/fan-out.md § Delegating reading and auditing | A report is evidence, not a finding. |

### Assurance traps

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R67 | an exit code piped through tail or tee reports the pipe's status | COVERED | docs/runbooks/gate.md § Running it | Capture the exit code itself: `<gate> > <log> 2>&1; rc=$?`, then branch on `rc` and read the result line |
| R67 | (same) | COVERED | docs/framework/FRAMEWORK.md § 8.5 Verification-state guards | exit-code hygiene: no piping through `tail`/`tee` |
| R68 | date-stamp every measured number; re-measure rather than difference | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P5 | with its date on the line |
| R68 | (same) | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P5 | Re-measure; never difference against a recorded number. |
| R69 | cite a symbol that exists; grep it first | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P3 | Code is cited as `file::symbol`. |
| R69 | (same) | COVERED | docs/framework/FRAMEWORK.md § 8.2 Trace and existence guards | every file, `file::symbol` and route named in the |
| R70 | sabotage a new check and watch it go red; prefer a mechanical refusal over a doc warning | COVERED | docs/framework/FRAMEWORK.md § 1. Principles, P7 | Sabotage what a guard protects and watch it go red before believing it. |
| R70 | (same) | COVERED | docs/framework/FRAMEWORK.md § 0.2 Stance | Mechanical refusal beats a written warning. |

**Tally** (rule ids, counted by the § 5 checker on 2026-11-08): 70 rules: 41 COVERED, 4 DIVERGES, 4 GAP, 17 MACHINE, 1 HARNESS, 3 DROP.

## 2. Where the global file and the framework disagree

None of these is settled here: each is the owner's preference, and the pasted text applies machine-wide (DEC-319).
In a framework repo the pointer section of § 4 defers to the repo's contract; the optional baseline for repos
without the framework keeps the owner's current words.

- **R60, the subagent model.** The global file makes `opus` the default ("`opus` by default, which is also the
  session default since 2026-10-07"). FRAMEWORK § 6.6 makes the default "the cheapest model that can do it" and
  leaves the names to the repo's contract (this repo: DEC-45, haiku for watchers, sonnet for bulk reading, opus
  for code and review). The `fable` half agrees. If the owner wants cheapest-viable everywhere, the baseline's
  model line is the one to change.
- **R24, HANDOFF.md in full.** The global file says read it "in full, right after `CLAUDE.md`". In a framework
  repo `context-engine orient` prints the banner, the board and the top item, and procedures § Session start reads
  the rest of `HANDOFF.md` "only if needed".
- **R51 and R66, first-hand checks.** The global file has the session re-run every BROKEN repro first-hand and
  verify first-hand what heads for a record. The framework sends a verifier agent that did not do the work, and
  the coordinator reads that agent's report (contract § Rules, the coordinator; release.md § After the trial).
  The halves of R66 about reconciling and "evidence, not a finding" agree word for word.

## 3. Framework-shaped rules no framework text holds

These stay in the global file, in § 4's "Not yet in the framework", until the kit carries them. Moving them is a
kit change (the byte-equal kit copy of each runbook, perhaps the contract and so a framework version bump), so it
is a follow-up item, not part of this one (DEC-320).

| id | rule | proposed home |
|---|---|---|
| R19 | the sweep's four classes, evidence required for SUPERSEDED and SALVAGE, "SALVAGE is the deliverable" | `docs/runbooks/fan-out.md` § Delegating reading and auditing (kit copy under `src/context_engine/kit/docs/runbooks/`), as the sweep auditor's verdict form; FRAMEWORK § 6.6 roster row "`.scratch/` sweep auditor" points at it |
| R20 | exclude the auditing agent's own report directory from the sweep | the same bullet |
| R30 | commit whenever the gate is green and the session changed something | contract § Rules (this repo already has it as DEC-22 in its `CLAUDE.md`) |
| R34 | keep CI/CD config changes out of feature branches unless that is the task | `docs/runbooks/procedures.md` § Push and CI |
| R10 | candidate: a session that starts a long-lived process owns stopping it, and names what it leaves up | `docs/runbooks/fan-out.md` § Watchers (it covers background jobs); the Docker form stays global as MACHINE |

R21 (the Recycle Bin) is a Windows fact, so it stays global as MACHINE; it sits beside R19 in § 4 because it is
the sweep's only undo.

## 4. Proposed global CLAUDE.md (paste whole)

What changes: the sections Concurrent sessions, `.scratch/`, HANDOFF.md, Git: gate, commit, push, Delegation and
Assurance traps go, because the framework holds what they say (§ 1), they are provenance (DROP), or their
machine facts and gaps moved to the sections below. Two shells, Python environments, Docker and CI pipelines are
copied verbatim from the live file. New: the framework pointer, the CI run-reading and install-trial recipes
(moved out of Git), Other repos, Harness facts, Not yet in the framework, and an optional baseline for repos
without the framework. Old file: 411 lines; proposed: 269 lines (measured 2026-11-08 by the § 5 checker).

One verbatim line keeps a pointer to a removed section: Docker's "often in the same repo (§ Concurrent
sessions)". It is left verbatim so the E6 check holds; when pasting, the owner may change it to "(§ Repos without
the framework)", whose first bullet now carries that rule, or drop the parenthesis.

````markdown
# Environment notes

Machine-wide operating notes. Repo-specific rules live in each repo's `CLAUDE.md`
and win where they conflict. Verified 2026-09-02 unless stated.

## Framework repos: their contract holds the method

A repo whose `CLAUDE.md` carries a `framework: <version>` line and imports
`@docs/framework/contract.md` runs the context-engineering framework. There, its contract and
its runbooks (`docs/runbooks/`) are the method: delegation and persistence, subagent models,
commit, gate and push, the CI watcher, the release install trial, `.scratch/` and evidence,
HANDOFF.md, sabotage. Where they differ from this file, they win. This file keeps what they
cannot hold (this machine's facts, below) and the few method rules no framework text holds yet
(§ Not yet in the framework). A repo without that line follows § Repos without the framework.

## Two shells — do not mix their syntax

Both a PowerShell tool and a Bash (Git Bash) tool are available. The wrong syntax
in either **fails silently or half-works rather than erroring**, so the damage
surfaces later in a commit message, a written file, or an argument.

The recurring one: `@'...'@` is a PowerShell here-string **only**. Bash reads `@'`
as a literal `@` plus a quote, so `git commit -m @'...'@` succeeds with a subject
line of `@`. In Bash use a heredoc (`git commit -F - <<'MSG' ... MSG`); in
PowerShell use the here-string with the closing `'@` at column 0.

| Intent | Bash | PowerShell 5.1 |
| --- | --- | --- |
| Read env var | `$VAR`, `$HOME` | `$env:VAR`, `$env:USERPROFILE` |
| Set env var for one command | `VAR=x cmd` | `$env:VAR = 'x'; cmd` |
| Discard stderr | `2>/dev/null` | `2>$null` |
| Escape character | `\` | backtick |
| Run B only if A succeeded | `A && B` | `A; if ($?) { B }` — **no `&&` in 5.1** |
| Null device | `/dev/null` | `$null` |
| Command substitution | `` `cmd` `` or `$(cmd)` | `$(cmd)` only |
| Multi-line string | heredoc `<<'EOF'` | here-string `@'...'@` |
| Test a path exists | `[ -f x ]`, `[ -d x ]` | `Test-Path x` |
| Loop over items | `for x in *; do … done` | `foreach ($x in …) { … }` |

PS 5.1 also has no ternary, no `??`, no `?.`. Pick the tool first, then write for
that shell; do not carry a snippet across without re-reading it.

**The two directions fail differently, and only one of them gets caught.** Bash
control flow in PowerShell (`if [ -f x ]`, `for x in *`, backtick substitution)
is a **parse error** — loud and immediate. PowerShell in Bash is the quiet one:
`@'…'@`, `$env:VAR`, `2>$null` and `Get-ChildItem`/`Test-Path` are all *valid
Bash* that mean something else or nothing at all, so the command exits 0 and the
damage surfaces later. **Suspect the Bash direction first.**

**Execution policy is `Restricted`** (all persisted scopes `Undefined`; no GPO
lock). A bare `.\script.ps1` or dot-source fails with `UnauthorizedAccess`. Run
`.ps1` files as `powershell -NoProfile -ExecutionPolicy Bypass -File .\x.ps1`, or
`Set-ExecutionPolicy -Scope Process -Bypass -Force` inside a session. Do not
assume PowerShell profiles run. (Claude Code's PowerShell tool runs at Process
scope `Bypass`, so this failure is invisible from inside the tool — it is real in
the user's own shell.)

Suppressing a `Write-Host` banner needs `6>$null`; `| Out-Null` does not catch the
information stream.

## Python environments

**Bare `python` is broken** — `python.exe`/`python3.exe` on PATH are Microsoft
Store redirector stubs and fail with "The system cannot find the path specified".
Never invoke bare `python`. **`conda` and `uv` are not on PATH either**; `pixi`
is (`~/.pixi/bin/pixi`).

- Conda entrypoint: `C:/Users/user/anaconda3/Scripts/conda.exe` (or `condabin/conda.bat`).
- **Convention: one conda env named after the repo folder, always lowercase**
  (`conda activate` is case-sensitive, so folder `SpeechEnhancement` → env
  `speechenhancement`). Envs live in `C:/Users/user/anaconda3/envs/<name>`.
- **Calling the env's interpreter by full path is the most reliable form:**
  `C:/Users/user/anaconda3/envs/<name>/python.exe`. `conda run` does **not**
  forward stdin, so piping into it fails.
- **If the env does not exist, ask before creating it.** Do not silently create
  one or fall back to another Python. Confirm the intended Python version first.
- Check before assuming: `C:/Users/user/anaconda3/Scripts/conda.exe env list`.

Known deviations (do not "fix" them): `SpeechEnhancement` is a uv project
(`uv sync` / `uv run`); `audio-workspace` uses pixi for **node only** plus
per-subproject uv venvs (`server/.venv`); `gitlab-admin-scripts` has no env and
runs on base conda (`C:/Users/user/anaconda3/python.exe`).

## Docker

Docker **is installed and working** on this laptop. It runs as Docker Engine
(`docker-ce`, Apache 2.0) inside WSL2 Ubuntu 26.04 - not Docker Desktop.

**Never install Docker Desktop**, and never suggest it. Its subscription terms
are a problem for this machine. If Docker looks broken or missing, it is not -
read the rest of this section first.

`docker` on the Windows side is a guard shim at `C:\Users\user\bin\docker.cmd`,
not the real CLI. It forwards **read-only** commands to WSL and **refuses**
anything that writes, builds, or runs containers, printing an explanation.

- Works from Windows: `ps`, `images`, `logs`, `inspect`, `version`, `info`,
  `stats`, `system df`, `volume ls`, `compose ps`, `compose logs`.
- Refused from Windows: `run`, `build`, `exec`, `rm`, `pull`, `push`,
  `compose up`, anything with `-v` / `--mount` / `--env-file`, and any argument
  that looks like a Windows path.

A refusal is **not** a sign Docker is missing or broken. It is deliberate:
Windows paths mean nothing to the Linux docker CLI, so bind mounts and build
contexts would break quietly rather than fail loudly. Do the real work inside
WSL: `wsl` then run docker normally, or `wsl docker <args>` for a one-off.

In Git Bash, `docker` is a function in `~/.bashrc` calling the same shim, because
Git Bash does not auto-resolve `.cmd`. The guard logic is `~/bin/docker-wsl-guard.ps1`
beside the shim. `~/bin` was appended to the user PATH, and the pre-change PATH is
backed up at `~/path-backup-before-docker-shim.txt`. A shim was chosen over relaxing
the execution policy.

Details: Ubuntu 26.04 (WSL2 default distro), Engine 29.7.2, Compose v5.5.0.
Daemon runs under systemd, enabled at boot. Linux user `user` is in the `docker`
group — **do not prefix `docker` with `sudo`**. Keep container projects on the
Linux filesystem (`/home/user/...`); `/mnt/c` works but is dramatically slower.
WSL memory is capped at 8GB + 2GB swap in `C:\Users\user\.wslconfig` — check that
first on an OOM.

### Turn it off when you are done — the laptop is shared with other sessions

Several Claude sessions run **concurrently across different repos** on this one
laptop, and often in the same repo (§ Concurrent sessions). Anything you start competes
with them for the same CPU and the same 8GB WSL cap, and none of them can see
what you left running. So a session that starts a long-lived process **owns
stopping it**:

- **Throwaway test containers** — stop them in the same session that started
  them, not "next time". `docker rm -f <name>`, or the repo's own stop flag
  (audio-workspace: `tools/local-postgres/start-test-postgres.sh --stop`).
- **`--keepalive` WSL sessions**, dev servers, watchers, `run_in_background`
  jobs — same rule. A held wsl.exe session exists only to keep a container
  alive; when the container goes, close it.
- **Cached images are fine to keep** (disk, not RAM). Running containers are not.
- If you deliberately leave something up because the user asked, **say so in the
  final message, by name**, so the next session knows what to kill.

`wsl docker ps` is the one-line check before you end a session. `wsl --shutdown`
reclaims the whole VM, but **ask first** — it kills every other repo's
containers too.

## CI pipelines — getting a token

Both tokens already exist in **Windows Credential Manager**; neither CLI is
logged in. **Never print a token value.**

**GitHub** — `gh` v2.97 is installed but not authenticated, and `GH_TOKEN` is
unset. Do not run `gh auth login` (interactive). Source the existing credential
per command, **from the Bash tool** (the PowerShell equivalent breaks: CRLF makes
`git credential fill` reject the input):

```bash
cd /c/Users/user/pycharmprojects/<repo> && \
export GH_TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p') && \
gh run list --limit 10
```

Shell state does not persist between calls, so re-source it in **every** command.
Then `gh run view <id> --json status,conclusion,workflowName`, `--log-failed`,
`gh run watch <id>`, `gh pr checks <n>`. Scopes are `gist, repo, workflow` —
`read:org` is missing, so `gh` warns and org-scoped commands may fail. Public
repos need no credential at all (60 req/hr): `curl -s
https://api.github.com/repos/<owner>/<repo>/actions/runs?per_page=5`.

**GitLab** — loader scripts live in `pycharmprojects/gitlab-admin-scripts/`
(`Set-GitLabToken.ps1` → `$env:GITLAB_TOKEN`, via `credread.ps1` P/Invoking
`advapi32!CredRead`). Because of the execution policy above:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. 'C:\Users\user\pycharmprojects\gitlab-admin-scripts\Set-GitLabToken.ps1' 6>$null
$h = @{ 'PRIVATE-TOKEN' = $env:GITLAB_TOKEN }
$proj = [uri]::EscapeDataString('csitsg/skillscape')   # URL-encode the full path
$pl = (Invoke-WebRequest "https://gitlab.com/api/v4/projects/$proj/pipelines?per_page=1" -Headers $h -UseBasicParsing).Content | ConvertFrom-Json
```

Then `/pipelines/:id` and `/pipelines/:id/jobs`, and `/jobs/:id/trace` for a raw
log. `glab` is not installed.

⚠ **PS 5.1 JSON-array traps** — one unrolling bug, two symptoms. Do **not** wrap
`ConvertFrom-Json` in `@()`: `@($r.Content | ConvertFrom-Json)` yields `Count=1`
whose `[0]` is itself an array, so `foreach` runs once. Do **not** pipe
`Invoke-RestMethod` straight into `Sort-Object`/`ForEach-Object` on a JSON array
either: it intermittently hands the whole array through as one item and you get
`Cannot convert "System.Object[]" ... to type "System.Int32"`. Use
`Invoke-WebRequest -UseBasicParsing` + `ConvertFrom-Json`, and accumulate with a
plain assignment or `$d = @(); $d += (...)`, which unrolls correctly.

GitLab remotes here: `skillscape`, `meme-backend`, `meme-frontend`,
`audio-workspace`, and `Farfield-Audio-Synthesis-Toolkit` (whose `origin` is
GitHub and whose GitLab remote is named `csitsg`).

### Reading a pushed commit's runs, and the release install-trial env

- **Reading CI runs:** GitHub: `gh run list --commit <sha>`, `gh run watch <id> --exit-status`, and
  on a failure `gh run view <id> --log-failed`. GitLab: poll `/pipelines?sha=<sha>`, then
  `/jobs` and `/jobs/:id/trace` for a failed job. Re-source the token in every command.
- **Release install-trial env:** `C:/Users/user/anaconda3/Scripts/conda.exe create -y -n
  <dist>-pypi-trial python=<the declared floor>` (this user request is the standing
  permission to create it), then `<env>/python.exe -m pip install <dist>==<version>` and
  nothing else. Work outside the repo (e.g. `$TEMP/<dist>-trial`) and confirm `<pkg>.__file__`
  is in the env's site-packages. Clean up: `conda.exe env remove -y -n ...`, confirm it is gone,
  delete the temp dir. Live on the index: `https://pypi.org/pypi/<dist>/<version>/json` returns 200.

## Other repos on this machine

- `SpeechEnhancement` and `skillscape` have no `.scratch/` and no ignore entry, so creating one
  there produces a *tracked* directory unless the ignore line is added first.
- `gitlab-admin-scripts` has been a git repo only since 2026-09-10 (one commit, "add
  everything"), and its `CLAUDE.md` doubles as its session log. Check that a file is actually
  tracked before treating git as its backup.
- `HANDOFF.md`: only some repos have one (`graph-reachability-zanzibar-index` is the fullest
  example). Do not create one unasked.

## Harness facts

- **To tell whose edit it is:** workflow subagent transcripts under the session's
  `subagents/workflows/<runId>/` record every `Write`/`Edit` call.
- **Not every agent CAN persist.** `Explore` has no `Write`/`Edit`, and its instructions forbid
  creating files through the shell, so it silently cannot comply. Use `general-purpose` or
  `claude` for persisted work. A write-capable agent has also been refused mid-run, so check
  the persisted file's size when the agent returns, and if it is missing or short, persist on
  receipt. `Explore` is still right for a sweep you will act on in the same turn.

## Not yet in the framework

Method rules no framework text holds yet. They apply in every repo, framework or not, until the
framework carries them.

- **`.scratch/` sweeps:** when a session finds a `.scratch/` holding more than its own run's
  output, send a read-only subagent to audit it before deleting anything. Give the agent these
  four classes, and require *evidence* for the middle two:

  | class | meaning | delete |
  |---|---|---|
  | DERIVABLE | copy of a tracked file, `.orig`/`.fixed` backup, `__pycache__`, gate log, full tree copy, draft of text since committed | yes |
  | SUPERSEDED | its conclusion IS already in a tracked file — **the agent must name the file and quote the line** | yes |
  | SALVAGE | a measurement, sweep table, census or adjudication found nowhere tracked | **no — it names the tracked file the finding belongs in** |
  | UNCLEAR | cannot tell; says what it would need to decide | no |

  **SALVAGE is the deliverable; bytes recovered are not.** The point of the sweep is to find
  the thing that was about to be lost. **Exclude the agent's own report directory** from the
  sweep, or it will cheerfully classify its own work-in-progress as garbage. Bulk deletes go to
  the **Recycle Bin**, not `rm -rf` — that is the only undo `.scratch/` has.
- **Commit on green:** when the repo's gate is green and the session changed something, commit —
  a green tree is the cheapest resume point. A read-only session commits nothing.
- Keep CI/CD config changes out of feature branches unless that is the task.

## Repos without the framework (optional: delete this section to take the gap whole)

- Several sessions share a tree: re-run `git status` and `git log -3` right before editing or
  committing; commit by path (`git commit -o <paths>`), never `git add -A`, never `git stash`.
  `HANDOFF.md` and the decision log are the collision points.
- Committing does not need permission; pushing, MRs and PRs do. Gate before every push; if the
  gate is red, say what is red and leave it.
- Every push gets a background CI watcher subagent, keyed on the pushed SHA, watch only,
  persisting to `.scratch/ci-watch/<sha>.md`; the push is not done until its verdict is in.
- A published release: confirm it is live, then a fresh-user install trial (env recipe in § CI
  pipelines); re-run every BROKEN repro first-hand; fixes ship as the next patch version.
- Delegate bulky reading for context, not parallelism; ask for verdicts plus `file::symbol`
  evidence; every agent persists incrementally to its own file; a report is evidence, not a finding.
- Subagent model: `opus` by default, `sonnet` for bulk reading or summarising, `haiku` for
  watching a CI run, `fable` only when the owner asks for it.
- Evidence leaves `.scratch/` for a tracked file the same hour.
- `HANDOFF.md`, where a repo has one: read it at session start; write back at session end
  (log entry, banner, rows, "Still owed:").
- No check is believed until it has been seen to fail; capture exit codes without a pipe;
  date-stamp measured numbers; cite symbols that exist.
````

## 5. How this was checked

The checker below is a throwaway script (not a tracked test: this doc freezes when its item closes, and frozen
provenance is never edited, so a pin to FRAMEWORK's wording would go red on every rewording; DEC-317). It was run
with the env interpreter, `-I`, and a fresh `PYTHONPYCACHEPREFIX`, from the repo root, as
`python -I check_ce40.py <this doc> ~/.claude/CLAUDE.md`. It checks: every quote of a row that names a file is a
whitespace-collapsed substring of `git show HEAD:<file>` (E2, E3); no COVERED or DIVERGES row has an empty file or
quote cell (E4: a `|` in a quote breaks its row); every GAP term is absent from the framework texts at HEAD; the
audited hash is the live file's (E5); every non-blank line of the global header, Two shells, Python
environments, Docker and CI pipelines sections is a line of the § 4 block (E6); exactly two lines open with four
backticks (E7); the § 4 block holds no dropped provenance (E8) and nothing token-shaped (E9); lines 1 to 10 name
this item and no other board id (E10); and the stated line counts and tally are what it measures.

```python
"""CE-40 checker: the audit doc's quotes, gaps and section 4 against HEAD and the live global file."""
import hashlib
import re
import subprocess
import sys
from collections import Counter

FENCE = "`" * 4
VERDICTS = {"COVERED", "DIVERGES", "GAP", "MACHINE", "HARNESS", "DROP"}
KEPT = ("# Environment notes", "## Two shells", "## Python environments", "## Docker", "## CI pipelines")
DROPPED = ("121M", "578d5f4", "0.0.2", "2026-07-28")
SECRETS = ("ghp_", "glpat-", "@gmail.com")
LIVING = ["docs/framework/FRAMEWORK.md", "docs/framework/contract.md"]


def show(path):
    return subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def collapse(text):
    return " ".join(text.split())


def main(doc_path, global_path):
    bad = []
    doc = open(doc_path, encoding="utf-8").read().split("\n")
    raw_global = open(global_path, "rb").read()
    glob = raw_global.decode("utf-8").replace("\r\n", "\n").split("\n")
    if glob and glob[-1] == "":
        glob = glob[:-1]

    # E10 and the liveness line
    ids = set(re.findall(r"CE-\d+", "\n".join(doc[:10])))
    if ids != {"CE-40"}:
        bad.append(f"E10 board ids in lines 1-10: {sorted(ids)}")
    if doc[2] != "ACTIVE-PLAN while CE-40 is open; freeze it when CE-40 closes.":
        bad.append("E1 line 3 is not the ACTIVE-PLAN line")

    # E2-E4: the verdict rows
    runbooks = subprocess.run(["git", "ls-tree", "--name-only", "HEAD", "docs/runbooks/"],
                              capture_output=True, text=True, check=True).stdout.split()
    living = {p: collapse(show(p)) for p in LIVING + [r for r in runbooks if r.endswith(".md")]}
    cache, first, quotes, absences = {}, {}, 0, 0
    sec1 = doc[doc.index("## 1. Verdict per rule"):doc.index("## 2. Where the global file and the framework disagree")]
    for line in sec1:
        if not re.match(r"^\| R\d+ \|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            bad.append(f"E4 broken row ({len(cells)} cells): {line[:60]}")
            continue
        rid, _rule, verdict, where, quote = cells
        first.setdefault(rid, verdict)
        if verdict not in VERDICTS:
            bad.append(f"bad verdict {rid}: {verdict}")
        path = re.search(r"(docs/[\w./-]+\.md)", where)
        if verdict in ("COVERED", "DIVERGES") and (not path or quote in ("", "-")):
            bad.append(f"E4 empty file or quote cell on {rid}")
            continue
        if quote.startswith("absent:"):
            for term in [t.strip() for t in quote[len("absent:"):].split(",")]:
                absences += 1
                hits = [p for p, t in living.items() if term.lower() in t.lower()]
                if hits:
                    bad.append(f"PRESENT {rid} {term!r} in {hits}")
        elif path:
            quotes += 1
            text = cache.setdefault(path.group(1), collapse(show(path.group(1))))
            if collapse(quote) not in text:
                bad.append(f"MISS {rid} {path.group(1)}")
    want = [f"R{i}" for i in range(1, len(first) + 1)]
    if list(first) != want:
        bad.append(f"row ids are not R1..R{len(first)} in order")
    counts = Counter(first.values())
    tally = ", ".join(f"{counts[v]} {v}" for v in ("COVERED", "DIVERGES", "GAP", "MACHINE", "HARNESS", "DROP"))
    tally = f"{len(first)} rules: {tally}"
    stated = re.search(r"^\*\*Tally\*\* \([^)]*\): (.*)\.$", "\n".join(doc), re.M)
    if not stated or stated.group(1) != tally:
        bad.append(f"stated tally differs; measured: {tally}")

    # E5: the audited hash
    sha = hashlib.sha256(raw_global).hexdigest()
    stated_sha = re.search(r"sha256 `([0-9a-f]{64})`", "\n".join(doc[:10]))
    if not stated_sha or stated_sha.group(1) != sha:
        bad.append(f"E5 global file changed since the audit: live sha256 {sha}")

    # E7: the section 4 fence
    fences = [i for i, l in enumerate(doc) if l.startswith(FENCE)]
    if len(fences) != 2 or doc[fences[0]] != FENCE + "markdown" or doc[fences[1]] != FENCE:
        bad.append(f"E7 lines opening with four backticks: {len(fences)}")
        return report(bad, quotes, absences, tally, 0, len(glob), 0)
    block = doc[fences[0] + 1:fences[1]]
    block_lines = {l.rstrip() for l in block}
    body = "\n".join(block)

    # E6: verbatim machine sections
    sections, name = {}, None
    for l in glob:
        if l.startswith("# ") or l.startswith("## "):
            name = l
        sections.setdefault(name, []).append(l)
    missing = 0
    for head, lines in sections.items():
        if head and head.startswith(KEPT):
            for l in lines:
                if l.strip() and l.rstrip() not in block_lines:
                    missing += 1
                    bad.append(f"E6 missing from section 4: {l.strip()[:70]}")

    # E8, E9
    for s in DROPPED:
        if s in body:
            bad.append(f"E8 dropped provenance in section 4: {s}")
    for s in SECRETS:
        if s in body:
            bad.append(f"E9 token-shaped text in section 4: {s}")

    counts_line = re.search(r"Old file: (\d+) lines; proposed: (\d+) lines", "\n".join(doc))
    if not counts_line or (int(counts_line.group(1)), int(counts_line.group(2))) != (len(glob), len(block)):
        bad.append(f"stated line counts differ; measured old {len(glob)}, proposed {len(block)}")
    return report(bad, quotes, absences, tally, missing, len(glob), len(block))


def report(bad, quotes, absences, tally, missing, old, new):
    for b in bad:
        print(b)
    print(f"checked {quotes} quotes and {absences} absent terms; {tally}")
    print(f"section 4: {missing} kept lines missing; old {old} lines, proposed {new} lines")
    print(f"{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
```

Its output on 2026-11-08, at HEAD `a67df78`:

```text
checked 72 quotes and 9 absent terms; 70 rules: 41 COVERED, 4 DIVERGES, 4 GAP, 17 MACHINE, 1 HARNESS, 3 DROP
section 4: 0 kept lines missing; old 411 lines, proposed 269 lines
0 problems
```

Sabotage, each run with a fresh `PYTHONPYCACHEPREFIX` and restored exactly afterwards (2026-11-08):

- **E2, a drifted quote.** Broke: R60's first quote, "can do it" changed to "can do them". The checker printed
  `MISS R60 docs/framework/FRAMEWORK.md`, `1 problems`, exit 1. Restored: `0 problems`, exit 0.
- **E6, a lost machine line.** Broke: the line ``is (`~/.pixi/bin/pixi`).`` deleted from the § 4 block. The
  checker printed ``E6 missing from section 4: is (`~/.pixi/bin/pixi`).`` and `stated line counts differ;
  measured old 411, proposed 268`, then `section 4: 1 kept lines missing`, `2 problems`, exit 1. Restored:
  `0 problems`, exit 0.
- **E1, the liveness line.** Broke: line 3's `ACTIVE-PLAN` written as `ACTIVE PLAN`. `context-engine lint` printed
  `G-D4 docs/evidence/global-claude-md-audit-2026-11-07e.md: declares no liveness in its first 10 lines`, exit 1
  (guards.py::liveness). Restored: `lint: clean`, exit 0.

The doc's sha256 was the same before the three runs and after the restores.
