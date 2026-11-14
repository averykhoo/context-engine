ACTIVE-PLAN: until CE-40 closes. Refreshes docs/evidence/global-claude-md-audit-2026-11-07e.md against the live file (456 lines, sha256 9798980e...01bf).

# Global CLAUDE.md audit, refreshed (CE-40)

Session 2026-11-14a, claude-code/claude-opus-5-5, 2026-11-14. Live file: the owner's global
`~/.claude/CLAUDE.md`, sha256 `9798980e618f3ef4a394681e3234bdb56017c612eb05b63fd928cea532e201bf`,
456 lines, read 2026-11-14. Checked against HEAD `989982a`. The 2026-11-07e audit (sha256
`7294a14c...0fb9`, 411 lines) is not edited; this doc replaces its § 4 proposal, which would now
delete 45 live lines if pasted. This doc proposes; a reviewer decides, and the owner pastes § 4 by
hand. Nothing here edits the global file. The owner delegated the trim (DEC-343 item 6).

## 1. What changed in the live file since the 2026-11-07e audit

**Method.** The audited 411-line file was recovered byte-exact from the 2026-11-07e session's
transcript (a Read result whose rebuilt text hashes to `7294a14c73f63a940a0087d34eea2c335cae2b8d9b78d5904cb72510d78b0fb9`),
then diffed against the live file with `diff` (2026-11-14). A second, independent check: every
non-blank line of the live header, Two shells, Python environments, Docker and CI pipelines
sections is a line of the old § 4 block (0 missing of 147, 2026-11-14), as the old audit's E6 said.

**Result (diff, 2026-11-14): three insertions, no deletion, no changed line.** 411 + 24 + 15 + 6 = 456.

| # | where (live file) | lines | what | new rule ids |
|---|---|---|---|---|
| C1 | new § Gemini API key (Google AI Studio, free tier), after § CI pipelines | 24 | the key's Credential Manager target, the loader, never print it, keep it (no rotation); the tracked scripts that call it and their conda env; free-tier quotas (measured 2026-11-11), a 503 counts, test with Flash Lite, `thinkingLevel` low | R72, R73, R74 |
| C2 | new § Hugging Face token, after C1 | 15 | the token's Credential Manager target, the loader, never print it, the pyannote terms accepted; the Python helpers that read it | R75, R76 |
| C3 | § Assurance traps, two bullets appended | 6 | never `bash <file>` a variable path without checking its extension; never background an `&&` chain, put it in one script and run that with `run_in_background` | R77, R78 |

Nothing in the six sections the old § 4 removed (Concurrent sessions, `.scratch/`, HANDOFF.md, Git,
Delegation, Assurance traps' first four bullets) changed, so R1 to R71 keep their verdicts, subject
to § 3 (whether the framework lines they cite still hold).

## 2. Verdicts for new and changed rules

The classes are the 2026-11-07e audit's (its § 1): COVERED, DIVERGES, GAP, MACHINE, HARNESS, DROP. New ids
continue from R71; R1 to R71 are not renumbered. A GAP row lists terms with 0 case-insensitive hits in
`docs/framework/FRAMEWORK.md`, `docs/framework/contract.md` and `docs/runbooks/*.md` at HEAD `989982a`
(counted 2026-11-14, whitespace collapsed, by a throwaway script, since `grep -iF` aborts in this Git Bash).

### Gemini API key (Google AI Studio, free tier) (C1)

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R72 | the key is the Credential Manager generic credential `gemini:aistudio`; the `credread.ps1` loader; never print it; kept on purpose, no rotation | MACHINE | - | absent: Gemini, never print, secret |
| R73 | the tracked scripts that call it live in `audio-workspace` `tools/demo-fixtures/`, conda env `audio-demo`; copy or import them rather than write a new client | MACHINE | - | - |
| R74 | free-tier quotas (measured 2026-11-11), a 503 still counts; test with a Flash Lite model; set `thinkingLevel` low | MACHINE | - | - |

R74 carries dated measurements, but they are the operating limits of the owner's account, not provenance for a
rule, so it is MACHINE, not DROP, and its numbers stay with their date.

### Hugging Face token (C2)

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R75 | the token is the Credential Manager generic credential `huggingface:hf`; same loader; never print it; the pyannote terms are accepted | MACHINE | - | absent: Hugging, never print |
| R76 | the Python helpers in `audio-workspace` (`demo_keys.py`, `diarise.py`, conda env `audio-demo`) | MACHINE | - | - |

### Assurance traps, two bullets (C3)

| id | rule | verdict | file § heading | quote |
|---|---|---|---|---|
| R77 | never `bash <file>` a path held in a variable without checking its extension | GAP | - | absent: bash <file>, held in a variable, its extension |
| R78 | never background an `&&` chain; put the chain in one script and run that with `run_in_background` | GAP | - | absent: background an, && chain, in one script |

Neither rule has a framework line. The nearest hits are not it: `run_in_background` appears twice
(docs/runbooks/fan-out.md § Watchers, "the coordinator's `run_in_background` shell until-loop", and
docs/runbooks/procedures.md § Push and CI, "a `run_in_background` until-loop"), both about the CI watcher's
loop; `&&` appears three times, once in docs/runbooks/gate.md § Running it ("a following `&&` runs on"),
which is R67's pipe trap, and twice in docs/runbooks/manual-mode.md as the gate's `&& context-engine lint`. R78 also leans on a harness fact (`run_in_background` is a Claude Code tool parameter) and a machine
incident (commit memory, 2026-10-21), so it would be HARNESS or MACHINE if it were not a method rule.

**Placement is the owner's, not a framework gap to close.** DEC-131 (owner, ACCEPTED) chose "You paste rules 1
and 2 into ~/.claude/CLAUDE.md", and DEC-343 item 5 ("help me add that") had them added on 2026-11-14. So § 4
keeps both bullets verbatim in the global file, and § 3 of the old audit (proposed framework homes) gets no row
for them: moving them into the kit would need a new owner call.

**Tally of new rules** (2026-11-14): 7 rules: 0 COVERED, 0 DIVERGES, 2 GAP, 5 MACHINE, 0 HARNESS, 0 DROP. With R1 to
R71 unchanged, the file's 78 rules: 41 COVERED, 4 DIVERGES, 6 GAP, 22 MACHINE, 2 HARNESS, 3 DROP.

## 3. Old audit quotes that no longer hold

Re-run 2026-11-14 at HEAD `989982a`, by the old checker's rules (a quote is a whitespace-collapsed substring of
`git show HEAD:<file>`; an absent term has 0 case-insensitive hits in the framework texts; a HARNESS quote is a
substring of the live global file):

```text
72 quotes, 71 still verbatim; 9 absent terms; 1 problems
MISS R60 docs/framework/FRAMEWORK.md: The repo's contract names the models.
```

All 9 GAP terms (R19, R20, R21, R30, R34) still have 0 hits, so no old GAP has been closed by the framework
since 2026-11-08. Both HARNESS quotes (R14, R71) are still lines of the live global file.

| id | old quote (FRAMEWORK.md § 6.6 Delegation and build rounds) | now | changed by | verdict |
|---|---|---|---|---|
| R60 | The repo's contract names the models. | The repo's contract names each tier's model. | `5f38ddd` (2026-11-11, CE-219: size floor and build ladder in § 6.6) | still DIVERGES |

The rewording strengthens the divergence rather than closing it: § 6.6 now reads "The default for delegated work
is the cheapest model that can do it, on three tiers: the least for a watcher, the reading tier for bulk reading
and a census, and the most for code and review" (verbatim at HEAD), against the global file's "`opus` by
default". R60's other two quotes, and every other row's quote, still hold verbatim. No verdict among R1 to R71
changes.

## 4. Proposed global CLAUDE.md (paste whole)

Built from the 2026-11-07e § 4 block (270 lines), changed in five places, nothing else (2026-11-14):

1. **§ Gemini API key** and **§ Hugging Face token** (C1, C2) are inserted whole and verbatim from the live file,
   after § CI pipelines and its install-trial subsection, where the live file has them.
2. **§ Assurance traps** is kept, with the two new bullets (C3, R77, R78) verbatim and a three-line lead that
   says where the four older traps went (R67 to R70, COVERED; § 5).
3. The framework-pointer section names § Assurance traps beside § Not yet in the framework as the second home
   of method rules kept here.
4. **§ Repos without the framework**, the baseline, now carries the owner's whole wording of three DIVERGES
   rules where the old proposal had shortened it: R24 and R25 ("in full, right after `CLAUDE.md`", "a task the
   user assigns overrides its ranking"), R60 (the `fable` clause, "or for open-ended design or taste
   judgement, and say why") and R66 ("reconciled, not averaged", and first-hand verification of what heads for
   an append-only history, a gate pin or a golden). R51 was already whole. This keeps every DIVERGES rule in the
   file, as the brief asked. The baseline's heading still offers to delete it (DEC-162 accepted that gap):
   deleting it drops those four rules for repos without the framework, and nothing else.
5. Nothing else moved. The Docker line "often in the same repo (§ Concurrent sessions)" is still verbatim and
   still points at a section this proposal removes; when pasting, the owner may change it to "(§ Repos without
   the framework)" or drop the parenthesis (as the 2026-11-07e audit said). Superseded by § 6: § 4 now
   carries "(§ Repos without the framework)".

Checked mechanically (§ 5): every one of the 215 lines of the live file's seven machine sections (the header,
Two shells, Python environments, Docker, CI pipelines, Gemini API key, Hugging Face token) is in the block, and
each section is there as one contiguous verbatim run; 31 fragments of the MACHINE, HARNESS, GAP and DIVERGES rules
that sat in removed sections are in it; no dropped provenance and nothing token-shaped. Live file: 456 lines;
proposed: 328 lines (measured 2026-11-14).

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
(§ Not yet in the framework, § Assurance traps). A repo without that line follows § Repos
without the framework.

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
laptop, and often in the same repo (§ Repos without the framework). Anything you start competes
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

## Gemini API key (Google AI Studio, free tier)

The owner's key is a **Windows Credential Manager generic credential, target
`gemini:aistudio`** (stored 2026-11-11), the same store and loader as the GitLab
token. **Never print it.** The owner keeps it on purpose (no rotation): "you'll
probably need it again later".

```powershell
. 'C:\Users\user\pycharmprojects\gitlab-admin-scripts\credread.ps1'
$env:GEMINI_API_KEY = [CredMan]::Get('gemini:aistudio')[1]
```

Working scripts that call it (transcribe whole audio files, translate echo-verified
batches, with retry and model fallback) are tracked in `audio-workspace`
`tools/demo-fixtures/` (`gemini_transcribe.py`, `gemini_translate.py`; README there),
run with the conda env `audio-demo`. They read `GEMINI_API_KEY`, then the credential
above. Copy or import them rather than writing a new client.

Free-tier quotas are tiny and **a 503 "high demand" answer still counts against
them** (measured 2026-11-11: ~20 requests/day for each Flash model, 500/day for
Flash Lite, 25/day for 3.5 Transcribe). Test the API with a Flash Lite model, never
with the model the real job needs, and set `thinkingLevel` low (default thinking
burned ~63K tokens per call).

## Hugging Face token

The owner's token is the **Credential Manager generic credential `huggingface:hf`**
(stored 2026-11-11, same loader as above). **Never print it.** It has the pyannote
`speaker-diarization-community-1` terms accepted, which `pyannote.audio` needs.

```powershell
. 'C:\Users\user\pycharmprojects\gitlab-admin-scripts\credread.ps1'
$env:HF_TOKEN = [CredMan]::Get('huggingface:hf')[1]
```

Python: `audio-workspace` `tools/demo-fixtures/demo_keys.py` (`hf_token()`,
`gemini_key()`) reads the env var, then the credential, with ctypes and no extra
packages; `diarise.py` beside it is a working pyannote run (conda env `audio-demo`).

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
- **Workflow model:** Workflow `agent()` calls inherit the main-loop model unless `model` is set.

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

## Assurance traps

The framework holds the four older traps (an exit code piped through `tail`/`tee`, date-stamped
numbers, citing a symbol that exists, sabotage before belief); in a repo without it, § Repos
without the framework carries them. These two no framework text holds; the owner put them
here, and they apply in every repo:

- ⚠ **Never `bash <file>` a path held in a variable without checking its extension.**
  A slip in the variable runs a non-script file as bash (adhoc AAR 2026-10-21,
  entry 13; context-engine CE-110, DEC-131).
- ⚠ **Never background an `&&` chain.** Put the chain in one script and run that
  with `run_in_background`. Suspected cause, not proven, of the laptop running out
  of commit memory on 2026-10-21 (same AAR, entries 19-21).

## Repos without the framework

- Several sessions share a tree: re-run `git status` and `git log -3` right before editing or
  committing; commit by path (`git commit -o <paths>`), never `git add -A`, never `git stash`.
  `HANDOFF.md` and the decision log are the collision points.
- Committing does not need permission; pushing, MRs and PRs do. Gate before every push; if the
  gate is red, say what is red and leave it.
- Every push gets a background CI watcher subagent (user instruction, 2026-10-07), keyed on the
  pushed SHA (allow ~1 min for runs to appear), watch only, persisting to
  `.scratch/ci-watch/<sha>.md`; it returns a verdict per run and, for a failed job, the failing
  step with the ~30 log lines around the first error; the push is not done until its verdict is in.
- A published release (user instruction, 2026-10-07): confirm it is live, then a fresh-user install trial (env recipe in § CI
  pipelines); re-run every BROKEN repro first-hand; fixes ship as the next patch version.
- Delegate bulky reading for context, not parallelism; ask for verdicts plus `file::symbol`
  evidence; every agent persists incrementally to its own file (user instruction, 2026-09-20); a report is evidence, not a finding:
  contradicted reports get reconciled, not averaged, and anything headed for an append-only
  history, a gate pin, or a golden gets verified first-hand.
- Read-only reading/audit agents of that shape, and `ultracode` / the `Workflow` tool for a real
  fan-out with a reconcile step, have standing approval (owner, 2026-09-20): do not ask first.
  Never use them to make coupled work "go faster".
- Subagent model: `opus` by default, `sonnet` for bulk reading or summarising, `haiku` for
  watching a CI run, `fable` only when the owner asks for it, or for open-ended design or taste
  judgement, and say why.
- Evidence leaves `.scratch/` for a tracked file the same hour.
- `HANDOFF.md`, where a repo has one: read it at session start, in full, right after `CLAUDE.md`;
  a task the user assigns overrides its ranking; write back at session end
  (log entry, banner, rows, "Still owed:").
- No check is believed until it has been seen to fail; capture exit codes without a pipe;
  date-stamp measured numbers; cite symbols that exist.
````

## 5. Line accounting

Measured 2026-11-14 on the live file (456 lines) and the § 4 block (328 lines):

| live section | live lines | in § 4 |
|---|---|---|
| header (`# Environment notes`) | 5 | kept verbatim |
| Two shells | 45 | kept verbatim |
| Python environments | 23 | kept verbatim |
| Docker (with Turn it off) | 59 | kept verbatim |
| Concurrent sessions | 21 | removed |
| `.scratch/` (with Sweeping it) | 54 | removed |
| HANDOFF.md | 14 | removed |
| Git: gate, commit, push | 62 | removed |
| CI pipelines | 51 | kept verbatim |
| Gemini API key | 24 | kept verbatim (new since 2026-11-07e) |
| Hugging Face token | 15 | kept verbatim (new since 2026-11-07e) |
| Delegation | 61 | removed |
| Assurance traps | 22 | the heading, a blank and the two new bullets (8 lines) kept verbatim; the four older bullets (14 lines) removed |

Kept verbatim: 230 live lines. Removed: 226 live lines (21 + 54 + 14 + 62 + 61 + 14). The block's other 98 lines
are the sections the 2026-11-07e proposal wrote (framework pointer, the CI run-reading and install-trial
subsection, Other repos, Harness facts, Not yet in the framework, the baseline) and the Assurance traps lead:
230 + 98 = 328.

What holds each removed section: one row per covering line, quoted verbatim from HEAD `989982a` (re-verified
2026-11-14, § 3). The R-ids are the 2026-11-07e audit's; its § 1 has every other row of each section. A rule of a
removed section that is not COVERED is in § 4 under the heading the last column names.

| removed section | id | file § heading | quote | the rest goes to |
|---|---|---|---|---|
| Concurrent sessions | R11 | docs/framework/FRAMEWORK.md § 1. Principles, P12 | Commit by path; never `git stash` in a shared tree; re-check `git status` right before committing. | R14 to Harness facts; R15 DROP |
| Concurrent sessions | R12 | docs/framework/FRAMEWORK.md § 1. Principles, P12 | working-state files must be safe with several writers | |
| Concurrent sessions | R13 | docs/framework/contract.md § Rules | never `git add -A`, never `git stash`: sessions may share the working tree. | |
| `.scratch/` | R16 | docs/framework/FRAMEWORK.md § 1. Principles, P10 | `.scratch/` is throwaway space: anything recorded only there is already lost. | R17 to Other repos; R19, R20, R21 to Not yet in the framework; R23 DROP |
| `.scratch/` | R18 | docs/runbooks/fan-out.md § Delegating reading and auditing | Agents audit; the session decides and deletes. | |
| `.scratch/` | R22 | docs/runbooks/fan-out.md § Delegating reading and auditing | the session deletes the run's scratch files once their conclusions are in tracked files (P10), in the same session. | |
| HANDOFF.md | R25 | docs/runbooks/procedures.md § Session start (§6.1) | an assignment overrides the ranking | R24 (DIVERGES) to the baseline; R28 to Other repos |
| HANDOFF.md | R26 | docs/framework/FRAMEWORK.md § 6.7 Promotion and demotion | when it becomes a durable rule (the contract keeps a pointer) | |
| HANDOFF.md | R27 | docs/framework/contract.md § Procedures | As soon as every task the owner asked for is done, run the clean close | |
| Git | R29 | docs/framework/FRAMEWORK.md § 1. Principles, P8 | A local commit or a record write is cheap to undo | R30, R34 to Not yet in the framework; R37, R45 to CI pipelines' subsection; R51 (DIVERGES) to the baseline; R54 DROP |
| Git | R31 | docs/framework/FRAMEWORK.md § 6.8 Push and CI | push only with permission; | |
| Git | R32 | docs/runbooks/procedures.md § Push and CI (§6.8) | never push red or unverified | |
| Git | R33 | docs/runbooks/gate.md § Running it | Red: say what is red and leave it. Never commit on a red gate to make progress look verified | |
| Git | R35 | docs/framework/FRAMEWORK.md § 6.8 Push and CI | the push is not done until the watcher reports; | |
| Git | R36 | docs/runbooks/procedures.md § Push and CI (§6.8) | the watcher finds runs by hash, not "the latest run", which may be another session's | |
| Git | R40 | docs/runbooks/fan-out.md § Watchers | only watches: no fix, no re-run, no cancel, no push. | |
| Git | R44 | docs/runbooks/release.md § The fresh-user install trial | Every published release, once it is live, gets a background agent that installs the published artifact the way a stranger would. | |
| Git | R53 | docs/runbooks/release.md § Tag, publish, confirm | A version already on the index is never reused, and a pushed tag is never moved | |
| Delegation | R57 | docs/runbooks/fan-out.md § Delegating reading and auditing | would doing it inline flood the agent's context with file contents? | R60, R66 (DIVERGES) to the baseline; R63's harness half and R71 to Harness facts |
| Delegation | R58 | docs/runbooks/fan-out.md § Delegating reading and auditing | the verdict form (`file::symbol` evidence, never file dumps) | |
| Delegation | R61 | docs/framework/contract.md § Rules | needs no per-request opt-in when it keeps the session's own context and tokens down | |
| Delegation | R62 | docs/runbooks/fan-out.md § Delegating reading and auditing | each finding is appended as it lands, not buffered to the end | |
| Delegation | R63 | docs/runbooks/fan-out.md § Delegating reading and auditing | Only an agent that can write files can persist (not `Explore`). | |
| Delegation | R65 | docs/runbooks/fan-out.md § Delegating reading and auditing | the session deletes the run's scratch files once their conclusions are in tracked files | |
| Assurance traps, four older bullets | R67 | docs/runbooks/gate.md § Running it | Capture the exit code itself: `<gate> > <log> 2>&1; rc=$?`, then branch on `rc` and read the result line | R77, R78 stay in § 4's Assurance traps |
| Assurance traps, four older bullets | R68 | docs/framework/FRAMEWORK.md § 1. Principles, P5 | Re-measure; never difference against a recorded number. | |
| Assurance traps, four older bullets | R69 | docs/framework/FRAMEWORK.md § 1. Principles, P3 | Code is cited as `file::symbol`. | |
| Assurance traps, four older bullets | R70 | docs/framework/FRAMEWORK.md § 1. Principles, P7 | Sabotage what a guard protects and watch it go red before believing it. | |
| Assurance traps, four older bullets | R70 | docs/framework/FRAMEWORK.md § 0.2 Stance | Mechanical refusal beats a written warning. | |

These rows are a sample of each section's covering lines, not all 41 COVERED rows: the full per-rule table is the
2026-11-07e audit's § 1, whose quotes § 3 re-verified.

**How this was checked.** Throwaway scripts in .scratch/ce40-refresh/ (gitignored; run 2026-11-14 with the env
interpreter and `-I`): one rebuilt the audited file from the 2026-11-07e transcript and matched its sha256 (§ 1);
one re-ran the old audit's quote and absent-term checks at HEAD (§ 3); one built the § 4 block; one checks the
§ 4 block against the live file: each machine-section line present (M1), each machine section one contiguous
verbatim run (M2), the 31 rule fragments (F), no dropped provenance (E8), nothing token-shaped (E9), and exactly
one four-backtick fence pair (E7). Its run on this doc gave `live 456 lines; proposed 328 lines; 215
machine-section lines checked (blank included); 31 fragments checked; 0 problems`, exit 0. The § 5 quotes were
checked the same way as § 3's: `29 quotes checked; 0 problems`, exit 0 (sabotaged: R18's "deletes" changed to "removes" gave `MISS R18`, exit 1).

Sabotage (2026-11-14, each on a copy of the block, with a fresh `-X pycache_prefix`): a Gemini quota line deleted
gave M1 and M2 red, exit 1; R78's last line deleted gave `F R78 GAP fragment missing`, exit 1; R24's "in full"
removed gave `F R24 DIVERGES fragment missing`, exit 1; a fake `glpat-` token inserted under the Hugging Face
heading gave E9 and M2 red, exit 1; one blank line of the Hugging Face section changed to text gave M2 red, exit
1. The first R78 run crashed printing the warning sign (the console is cp1252), so it went red for the wrong
reason; the checker now writes UTF-8, and its re-run went red for the right one.

## 6. Review (2026-11-14a)

fable reviewed this proposal for the owner's delegated call (DEC-343 item 6): APPLY WITH CHANGES. Its four changes are made in § 4 above: the baseline heading loses "(optional: delete ...)", since an agent reads it as making the rules optional; the Docker pointer names § Repos without the framework, not the removed § Concurrent sessions; the 2026-09-20 standing approval for read-only agents and the Workflow tool is kept in the baseline, its only home being otherwise contract.md, which a repo without the framework never reads; and the dated "user instruction" markers, plus the CI watcher's return shape, are restored on three baseline bullets. fable spot-checked 4 removed rules against their framework quotes (all hold) and diffed § Two shells and § Docker byte-identical. Applying § 4 to the global file waits on the owner, because the edit rewrites a file every session on the machine reads.
