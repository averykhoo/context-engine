# Session ledger

Append-only, newest first, one entry per session without exception (FRAMEWORK §7.1). Kinds:
`close`, `pause`, `foreign` (human commits reconciled), and, once the engine mints keys, `open`
and `abandoned`. Until then (DEC-7) the session key is minted by hand at write-back as
`max(newest key here, HANDOFF banner key) + 1 letter`.

---

## 2026-10-17c · kind: open

- **opened:** 2026-10-17T19:50:22+08:00 by claude-code/claude-opus-5-5

---

## 2026-10-17b · kind: close

- **rows:** DEC-51 new; CE-43 LATER->NOW, dep CE-7 removed, dep CE-98 added; CE-93 NOW->NEXT; CE-98
  new; ASK-7..ASK-14 new and raised
- **receipts:**
  - guards: lint clean; gate status --require code green (no code changed)
  - read: audio-workspace CLAUDE.md, src/__tests__ doc-shape tests, decisions.md D-221; CE-43;
    procedures § Intake
  - asked: Owner: remove aw-owner-1014; full migration of audio-workspace now with a backup; vitest
    and smoke before push, not per commit; fable review of the recommendations and plan
- **summary** (the owner digest):
  - Removed the aw-owner-1014 worktree (merged into main); its junctions were unlinked first and
    main's node_modules checked intact (npm ls clean)
  - DEC-51 records the owner's direction: full migration of audio-workspace now, backup first,
    vitest and smoke before push; CE-43 is NOW
  - CE-98 filed, A reproduced first-hand: decision import silently drops text after inner ##
    headings (5,344 lines of audio-workspace's log), folds amendment headings into the wrong
    decision, takes bare dates as actors
  - Fable review (owner asked) agrees with the four recommendations; plan changes in CE-43's log:
    pre-init commit, rehearsal on a clone, line-conservation check, one-commit freeze, gate scope
    all with tsc + lint
  - Owed by owner: ASK-7..ASK-14, ASK-14 first (does DEC-51 lift the hold for the CE-98 engine fix);
    wip/owner-1014 branch kept, merged, delete if wanted
  - Scratch kept on purpose: .scratch/aw-onboard (assessment, importer probes, fable review);
    conclusions are in CE-43, CE-98 and the asks
- **Still owed:**
  - nothing

---

## 2026-10-17a · kind: close

- **rows:** none
- **receipts:**
  - guards: none (read-only session)
  - read: CE-43, CE-7, procedures.md § Bootstrap (via agent); audio-workspace tree (read-only)
  - asked: Owner asked what onboarding audio-workspace (the transcription app) onto context-engine
    would take, and whether it is straightforward
- **summary** (the owner digest):
  - Read-only assessment: onboarding audio-workspace is hard, about 5-10x the adhoc trial; CE-43
    already tracks it, behind CE-7 and the trial hold (CE-79, ~2026-10-21)
  - Main costs: 304-entry decisions.md (1.96 MB) is refused by decision import; HANDOFF.md 1660
    lines; repo's own doc-shape tests (claudeMdShape, handoffShape) fight the kit caps; node+python
    gate needs a wrapper
  - Agent-reported, not yet verified first-hand: decisions.py::parse_entries ends an entry at an
    inner '## ' heading, silently dropping text; worth filing as an engine bug
  - aw-owner-1014 is a worktree of audio-workspace on wip/owner-1014, clean and fully merged into
    main (14 behind, 0 ahead); safe to remove
  - Owed by owner: wait for CE-79 or lift the hold; import all decisions or freeze decisions.md as
    routed history; keep docs/issues/ as tracker; raise caps or prune; rewrite or retire doc-shape
    tests
  - Agent report kept at .scratch/aw-onboard/assessment.md (gitignored) until the owner decides
- **Still owed:**
  - nothing

---

## 2026-10-16a · kind: close

- **rows:** CE-92, CE-27, CE-93, CE-95, CE-96, CE-97
- **receipts:**
  - guards: gate PASSED in 501.7s (848 passed in 498.80s) on g1/code:1f39dc9d5c872827; gate readers
    PASSED in 23.4s (177 passed) on g1/code+readers:9d1324850fd49355; linux gate: green on
    5fa4fcb8df7d (848 passed); lint: clean
  - read: orient; procedures.md Session start, Housekeeping, Clean close, Push and CI; task show
    CE-27, CE-83, CE-92, CE-93
- **summary** (the owner digest):
  - CE-92 done (5581060, 4618f1f): clean close step 7 is lint + gate status, re-running only the
    readers after the close's own writes (a review finding).
  - CE-27 done (c901367, 5fa4fcb): doc freeze, doc archive, task close refuses an unfrozen
    ACTIVE-PLAN; review found archive refusals left a half-move, fixed; stale plugin-design plan
    frozen.
  - Owner picked CE-93 as NOW; DEC-50 holds it to about 2026-10-21, which the recommendation missed:
    confirm before starting (CE-93 Traps).
  - Filed CE-95 (CE-27 review small fixes), CE-96 (doc archive beyond whole docs), CE-97 (flag plans
    left open by by-hand closes).
  - Coordinator pattern worked: every task and fix went to an agent, and each review agent found a
    real gap the task agent had missed (DEC-44).
  - MCP server ran pre-CE-27 code and refused writes ([working] archive key): restart Claude Code
    before using MCP tools.
  - Owed: push (owner approved) and its CI verdict, done right after this close.
- **Still owed:**
  - push to origin and the CI watcher's verdict

---

## 2026-10-15e · kind: close

- **rows:** DEC-50, CE-29, CE-91, CE-92, CE-93
- **receipts:**
  - guards: lint: clean; gate status --require code: green (code covered on g1/code:107d5f6ac8cef3de
    by the all run of 2026-10-15T14:17:37+08:00); no code changed this session
  - read: CE-29, CE-91, CE-92, CE-93, DEC-43, procedures.md § Intake and § Clean close
  - asked: none
- **summary** (the owner digest):
  - Walked the owner through 2026-10-15d's open items; DEC-50 records all three answers verbatim.
  - CE-29: trap homes by lifetime accepted (task ## Traps, hazard board row, register INV-n; never
    the banner). Spec text stays under the CE-7 hold.
  - CE-92 released from the CE-7 hold; CE-93 stays held until CE-79's feedback; CE-91 goes with
    CE-83.
  - close-without-asking auto-memory deleted (DEC-31 is in CLAUDE.md); multi-task-delegation stays
    until CE-83.
  - 2026-10-14g was already abandoned by 2026-10-15d: nothing to do.
  - Records only; no code changed. Still unpushed: CE-41, CE-87 and the 2026-10-15b to e records.
- **Still owed:**
  - nothing

---

## 2026-10-15d · kind: close

- **rows:** none (ledger only: 2026-10-14g abandoned)
- **receipts:**
  - guards: lint clean; gate readers PASSED 173 in 13.7s on g1/code+readers:1d4c5be1bd14ddb3; code
    scope unchanged since the 2026-10-15 all run
  - read: orient (open-sessions section), procedures.md § Housekeeping, session-log.md
- **summary** (the owner digest):
  - Owner: close all sessions, no other agent running. 2026-10-14g marked kind: abandoned by hand
    (procedures § Housekeeping; G-W11 not built); its work was carried by 2026-10-15a, so no baton.
  - No sessions are open now.
- **Still owed:**
  - .scratch/wf-2026-10-14g and wf-2026-10-15a not swept (from 2026-10-15a)
  - Push of the unpushed commits since 5587731: ask first; linux_gate before

---

## 2026-10-15c · kind: close

- **rows:** US-12, DEC-47, DEC-48, DEC-49, CE-90, CE-91, CE-92, CE-93, CE-94, CE-29, CE-40, CE-47
- **receipts:**
  - guards: lint clean; gate status: code covered (all run 2026-10-15T14:17); gate readers PASSED
    173 in 10.8s on g1/code+readers:417dcd128bd86e2e
  - read: orient (hook) + FRAMEWORK.md (most sections) + procedures.md; HANDOFF not opened
- **summary** (the owner digest):
  - Management-theory review of the framework (read-only analysis in chat): strong on document
    control and error-proofing, weak on Check/Act (AAR, review, metrics).
  - Owner words recorded: US-12 amended (AAR + periodic review, apply to the framework itself);
    DEC-47 incidents cited by rules; DEC-48 who decides by reversibility; DEC-49 FRAMEWORK.md is for
    using the framework, not history.
  - Filed LATER: CE-90 AAR/periodic review, CE-91 reversibility into P8, CE-92 close step 7 drops
    the second full gate, CE-93 archive + rewrite FRAMEWORK.md, CE-94 incident citations.
  - dedupe-3/4/5/7 findings logged on CE-47 and CE-40; dedupe-6 trap-home recommendation logged on
    CE-29 (owner's word pending).
  - Kit/FRAMEWORK edits in CE-91/92/93 wait on the CE-7 hold unless the owner lifts it.
  - AAR: the redundancy subagent could not write its report file (harness refused Write); the report
    was taken back on receipt and verified first-hand, two of its claims overturned.
- **Still owed:**
  - Owner: confirm or redirect the CE-29 trap-home recommendation
  - Owner: whether CE-91/CE-92/CE-93 may proceed before the CE-7 trial lifts the kit hold
  - Memory: prune close-without-asking (DEC-31 is in CLAUDE.md); keep multi-task-delegation until
    CE-83 lands

---

## 2026-10-15b · kind: close

- **rows:** CE-41,CE-87,CE-27,CE-88,CE-89,CE-7
- **receipts:**
  - guards: gate PASSED in 291.0s (827 passed in 289.90s) on g1/all:e5b57b0436445ddf,
    g1/code:107d5f6ac8cef3de; lint: clean
  - read: orient (hook), task list, procedures.md session start and clean close
- **summary** (the owner digest):
  - CE-41 done (ea14d74): G-D3 resolves bare names only among files git does not ignore; the
    ambiguous-name half not built (AC-71)
  - CE-87 done (34ea268): lock timeout restarts on each hand-over; root cause an unfair lock summing
    holds under load
  - CE-27 promoted to NOW at the owner's word; CE-88 (ids_in_use under the lock) and CE-89 (frozen
    wording) filed
  - Owner: the adhoc trial keeps its pinned kit; feedback integrated later (CE-7 log)
  - MCP server ran stale code (refused [gate]); the CLI was used; restart Claude Code
  - Owner: session 2026-10-14g still open, functionally dead (2026-10-15a carried its work); abandon
    on your word
  - Not pushed: 4 commits wait on a push request (linux_gate first)
- **Still owed:**
  - push of ea14d74..HEAD (ask first; linux_gate before); abandoning 2026-10-14g needs the owner's
    word

---

## 2026-10-15a · kind: close

- **rows:** CE-64,CE-77,CE-78,CE-81,CE-83,CE-84,CE-85,CE-86,CE-87
- **receipts:**
  - guards: Windows: 825 passed in 491.68s, rc=0; Linux (tools/linux_gate.py 5587731): 825 passed in
    186.13s, green; lint clean (2026-10-15)
  - read: CLAUDE.md, contract, procedures.md, CE-83, DEC-43, agent reports in
    .scratch/wf-2026-10-15a
- **summary** (the owner digest):
  - Resumed 2026-10-14g's fan-out after a Windows restart (DEC-45): CE-64, CE-77, CE-78, CE-81
    fixed, reviewed, merged, closed
  - Pushed main 0a6eaa3..5587731 on DEC-46; CI gate run 38681332642 green; haiku watcher
  - Cheapest-model rule exists (FRAMEWORK §6.6) but CLAUDE.md names no model, so sessions fall
    through to the global opus default: on CE-83
  - CE-83 widened: CI watcher's model and full-log step; CE-84 session --follows link; CE-85
    MCP_TIMEOUT doc; CE-86 linux_gate from worktree
  - CE-87 to NOW: the concurrent-allocation lock test fails under parallel-gate load (30 s timeout)
  - CE-78 F1 weakens one refusal (code+readers is advisory); kit contract's git commit -o sentence
    not narrowed: owner's call, raise with CE-83
  - Process note: an engine write mid-merge by another agent is safe (commits by path) but worth
    telling the agent
- **Still owed:**
  - Session 2026-10-14g still shows open (cut off by the restart; its work is carried and done here)
  - .scratch/wf-2026-10-14g and wf-2026-10-15a not swept

---

## 2026-10-14g · kind: abandoned

- **opened:** 2026-10-14T19:49:23+08:00 by claude-code/claude-opus-5-5
- **abandoned:** 2026-10-15d: never closed or paused (cut off by a Windows restart; 2026-10-15a carried its work; the owner confirmed no other agent is running)

---

## 2026-10-14f · kind: close

- **rows:** CE-7 (trial started), CE-79 (check-back logged), CE-82 new and closed, DEC-31 amended
- **receipts:**
  - guards: gate green: 718 passed in 208.12s (2026-10-14); lint clean
  - read: kit contract.md, procedures § Clean close, FRAMEWORK §6.3, DEC-31, procedures § Push and
    CI
- **summary** (the owner digest):
  - Owner: the adhoc trial is running; CE-7 and CE-79 say it started 2026-10-14 and we check back
    about 2026-10-21; CE-7's title no longer says worktree.
  - Owner: close eagerly as soon as all tasks are done (DEC-31 amended); CE-82 put the rule in the
    always-loaded kit contract, procedures § Clean close, FRAMEWORK §6.3 and CLAUDE.md.
  - Push of context-engine main (owner: now, this repo only; adhoc stays local), after the gate and
    tools/linux_gate.py on the pushed commit; CI watcher started.
- **Still owed:**
  - CI verdict for the push (watcher); CE-7 check-back about 2026-10-21 (CE-79)

---

## 2026-10-14e · kind: close

- **rows:** CE-7 (moved onto adhoc main), DEC-42 new
- **receipts:**
  - guards: gate green: 717 passed in 187.21s (2026-10-14); lint clean
  - read: CE-7, adhoc .claude/settings.local.json, adhoc banner
- **summary** (the owner digest):
  - Owner: the trial belongs in adhoc's own folder, not a worktree, and the worktree goes (DEC-42);
    this also makes CE-7's merge decision.
  - adhoc main fast-forwarded to eef0ecc; worktree and branch deleted (junctions unlinked first,
    main's data intact); engine env rebuilt in adhoc at 38ed38e.
  - adhoc: MCP server registered for its folder; orient hook merged into its settings (owner: yes,
    DEC-32); adhoc session 2026-10-14b closed with the banner refreshed.
  - After-action: confirm where the owner wants a trial to run before building it; read banner text
    through UTF-8 (a cp1252 pipe turned the section sign into mojibake, caught before writing).
- **Still owed:**
  - CE-7: real Claude Code sessions in adhoc (INV-31 probes), scoring (CE-79); nothing pushed

---

## 2026-10-14d · kind: close

- **rows:** CE-7 (cut over on adhoc's trial branch), CE-79 new, CE-80 new, CE-81 new, DEC-41 new,
  DEC-1 amended
- **receipts:**
  - guards: gate green: 716 passed in 203.39s (2026-10-14); lint clean
  - read: CLAUDE.md, docs/framework/contract.md, CE-7, DEC-1, kit README § 1-Hook,
    docs/evidence/adhoc-dryrun-2026-10-14.md, procedures § Clean close
- **summary** (the owner digest):
  - Owner: the engine runs inside the adhoc repo; settled as DEC-41 (a pinned, non-editable engine
    env in the target repo's folder, gitignored), amending DEC-1.
  - CE-7: adhoc cut over on branch context-engine-trial (worktree adhoc-microphone-array-ce): kit at
    38ed38e, DEC-1..68, AD-1..14 + ASK-9, HANDOFF 605 -> 78 lines; adhoc gate green.
  - CE-79 filed: follow up on the trial about 2026-10-21. CE-80, CE-81 filed from trial findings;
    CE-81 waits for CE-7 (no kit edits mid-trial).
  - MCP server registered for the worktree (local scope; connects); the hook was already there.
    adhoc main is untouched until the merge.
  - After-action: register MCP during the cutover, not after; tell the owner which folder the trial
    runs in; close without asking when the work is done (DEC-31).
- **Still owed:**
  - CE-7: real Claude Code sessions in the adhoc worktree (INV-31 probes), scoring (CE-79), owner's
    merge decision; nothing pushed

---

## 2026-10-14c · kind: close

- **rows:** CE-77 filed; CE-78 filed
- **receipts:**
  - guards: gate pytest -q green, 714 passed in 247.54s (2026-10-14); CLI lint clean
  - read: CLAUDE.md, contract, CE-7, procedures.md § Clean close, zanzibar docs/gate-runbook.md § 4
    and scripts/gate_status.py
- **summary** (the owner digest):
  - Advised: CE-7's cutover runs from this repo (--root the adhoc worktree); its trial sessions must
    be fresh Claude Code sessions started in adhoc, not subagents from here.
  - Filed CE-77 (NEXT, after CE-7): procedures and repo adoption as skills, bundled with the
    SessionStart hook and MCP server as a Claude Code plugin; the contract stays always-on.
  - Filed CE-78 (NEXT, after CE-7): the code gate runs only when its scope changed, proven by a per-
    scope content hash on each gate run's result (zanzibar's gate_status.py shape); no framework
    edits until CE-7 is done (owner).
  - Concurrent session 2026-10-14d: each session's engine commit carried the other's uncommitted op
    lines (a1c22b5, 1cbeb52); nothing lost.
  - The MCP lint reported G-D12 (NFRs, residual-risk register) while the CLI lint was clean: the MCP
    server is probably running engine code older than the source, since /clear does not restart it.
- **Still owed:**
  - Confirm the MCP/CLI lint disagreement (G-D12) is a stale MCP server: restart Claude Code, then
    run lint through both.

---

## 2026-10-14b · kind: close

- **rows:** ASK-6 answered as DEC-40; AC-42 reworded
- **receipts:**
  - guards: gate pytest -q green, 710 passed (2026-10-14); lint clean
  - read: CLAUDE.md, contract; context carried from 2026-10-14a
- **summary** (the owner digest):
  - Owner answered ASK-6 (DEC-40): AC-42's foreign-prefix clause now describes DEC-37's
    rename-with-alias instead of a refusal; the rest of AC-42 is unchanged.
- **Still owed:**
  - push needs the owner's yes

---

## 2026-10-14a · kind: close

- **rows:** CE-69..CE-76 created; CE-51, CE-69, CE-70, CE-73, CE-74, CE-75, CE-76 closed; ASK-6
  created; comments on CE-7, CE-46, CE-47, CE-56; INV-70..INV-83 filed
- **receipts:**
  - guards: gate pytest -q green, 708 passed (2026-10-14); lint clean; linux_gate run before push
  - read: CLAUDE.md, contract, orient (hook), HANDOFF.md in full, task show CE-7
  - asked: ASK-6 raised in chat
- **summary** (the owner digest):
  - Audited the framework for sync: 53 drifts across spec, kit, runbooks, records and deployability,
    every one verified (docs/evidence/sync-audit-2026-10-14.md); no blockers, gate green before.
  - Fixed them: FRAMEWORK.md marks unbuilt parts and matches the engine's names; kit, runbooks,
    CLAUDE.md, context.toml routes, README and HANDOFF agree (CE-69).
  - Dry-ran the adhoc cutover in a throwaway clone (docs/evidence/adhoc-dryrun-2026-10-14.md): 4
    blockers; CE-7's traps and commands updated; adhoc untouched.
  - Built for the trial: DEC-37 import renaming with resolvable aliases (CE-74); orient never cuts
    batons, sessions or questions and honours its cap on Windows (CE-75); init fixes (CE-51, CE-70);
    --file intake (CE-73); small fixes (CE-76).
  - Trimmed the banner so orient shows it whole; moved its two banner-only rules into CLAUDE.md.
  - Note: merging worktree commits with autocrlf writes kit files with CRLF; merge with
    core.autocrlf=false (CE-46).
- **Still owed:**
  - push needs the owner's yes; CE-71 and CE-72 (LATER) left from the audit

---

## 2026-10-13e · kind: close

- **rows:** DEC-39 recorded and amended (owner words); CE-68 filed and closed; banner set
- **receipts:**
  - guards: pytest -q: 635 passed in 163.71s (rc=0), lint inside it clean, on the tree of 0f1d071;
    tools/linux_gate.py on f8a19b4: 635 passed (git 2.55.0, Python 3.12.3); lint clean on f8a19b4
  - read: orient + the CE-68 census (9 readers) and reconcile + the apply review, all via workflows;
    FRAMEWORK §6.8 only first-hand
- **summary** (the owner digest):
  - Owner: DEC-39, rituals renamed procedures, and every strange turn of phrase in the framework
    corrected in one change; amended with the owner's answers (keep baton, liveness, rung; unify the
    component names).
  - CE-68: a census workflow found the odd phrasing across FRAMEWORK, runbooks, kit, repo docs and
    engine messages; one glossary was applied by five disjoint appliers, then reviewed.
  - The review caught rewritten Log entries in four open tasks (restored), meaning drift in a few
    rewrites and over-width runbook lines; all fixed before the gate.
  - rituals.md is procedures.md in repo and kit; G-D12 still counts a frozen map's Ritual column and
    the old component names (Invariants, Law / NFRs).
  - Guards: no living framework text says ritual (test_kit); the G-D12 aliases (test_guards);
    sabotaged red, tools/sabotage_ce68.py.
  - Left: REGISTER entries still cite rituals.md (CE-56 rewrites the entries as RISK-n); the old
    tools/sabotage_ce24/26 probes point at the old path (dated evidence).
- **Still owed:**
  - REGISTER.md entries citing rituals.md, under CE-56

---

## 2026-10-13d · kind: close

- **rows:** US-18 recorded (owner words); CE-67 filed and closed; AC-79, AC-80 drafted and tested;
  banner set
- **receipts:**
  - guards: pytest -q: 631 passed in 145.80s (rc=0), lint inside it clean, on main c4e5704;
    tools/linux_gate.py on c4e5704: 631 passed (git 2.55.0, Python 3.12.3)
  - read: orient + rituals § Push and CI, § Intake + gate.md + FRAMEWORK §6.8 + CI run 38417074413
    log + actions/runner-images install-git.sh
- **summary** (the owner digest):
  - Pushed 39e09ca on a green Windows gate; CI went red: 3 CE-55 tests in test_commit.py failed only
    on Linux.
  - Owner: US-18 (fix them, replicate CI locally, guard the class). tools/linux_gate.py runs CI's
    job on any commit in a runner-shaped container (WSL docker) and reproduced CI's exact three.
  - Causes: time.sleep patched on the module (Linux subprocess polls with it); the runner's
    /etc/gitconfig safe.directory = *; Windows text-mode stdin sends CRLF to git.
  - Fixed in CE-67 with guards: tests read no machine git config; no test patches a stdlib module;
    test_ci keeps linux_gate in step with the workflow. Footguns: docs/evidence/ci-
    divergence-2026-10-13.md.
  - Rule: CLAUDE.md § Gate now runs the Linux gate before every push; gate.md (kit) and FRAMEWORK
    §6.8 carry the method.
  - For the owner: 'rituals' reads as off-putting; a rename (procedures or checklists) would be a
    decision and a task, not yet recorded.
- **Still owed:**
  - a decision on renaming 'rituals', if the owner wants one

---

## 2026-10-13c · kind: close

- **rows:** CE-26, CE-45, CE-49, CE-33, CE-55 closed (INV-36..69); CE-50..66 filed; CE-7, CE-26,
  CE-27, CE-45, CE-55 commented; ASK-5 answered (DEC-37); DEC-36, DEC-38 recorded
- **receipts:**
  - guards: pytest -q: 626 passed in 179.13s (rc=0), lint inside it clean, on main 29b7662 plus the
    close's records and the fan-out.md line
  - read: orient + task show CE-45, CE-49, CE-33, CE-26, ASK-5 + FRAMEWORK §5.2, §5.5 + rituals §
    Clean close
  - asked: ASK-5
- **summary** (the owner digest):
  - Owner: DEC-36 (the engine commits at milestones, not every write), DEC-37 (ASK-5: rename
    imported ids, keep the number, old id an alias), DEC-38 (standard prefixes DEC, STORY, AC, ASK,
    RISK, GOAL, BATON, PAUSE; EXP, HAZ reserved; per-repo task prefix; CE-56).
  - Built, each by a task agent in its own worktree (build, review lenses, a skeptic, fix), merged
    and sabotaged first-hand: CE-26 method runbooks, CE-45 engine commits, CE-49 record retire,
    CE-33 G-D4/G-D5 (measured first), CE-55 milestone commits with Closes: on task close.
  - For the owner: CLAUDE.md § Gate and § Rules still say git commit -o and gate every commit; the
    kit contract now says commit through context-engine commit, with the engine's milestone commits
    the one ungated exception. CLAUDE.md wins where they differ: the owner to pick the wording.
  - For the owner: restart Claude Code; the running MCP server refuses this repo's new [guards]
    keys, so this session ran on the CLI. Agent-drafted criteria AC-71..78 unread.
  - Found: agent commits put Session: outside git's trailer block (CE-64, NEXT); foreign reconcile's
    baseline drifts under milestones (CE-65); the MCP stdio test is a false red in worktrees
    (CE-62).
  - CE-7 (adhoc trial) is unblocked: adhoc's session ended; the owner runs it in a new session.
  - AAR: review agents must run in the foreground (a background child died with its parent's return,
    CE-45 round 1; now in fan-out.md); a stale MCP server goes from refusing writes to refusing
    every call when config keys are added.
- **Still owed:**
  - CLAUDE.md § Gate and § Rules wording after CE-55: the owner's call (the kit contract changed;
    CLAUDE.md wins where they differ)
  - .scratch/ holds older sessions' files (private-surveys, redaction-2026-10-09, w-*.md, banner-*):
    not swept this session; needs an audit agent before any delete

---

## 2026-10-13b · kind: close

- **rows:** CE-38 closed (bootloader; INV-28..32), CE-25 closed (intent-chain guards; INV-33..35);
  CE-7 to NOW; ASK-3, ASK-4 answered (DEC-33, DEC-32); ASK-5 filed and raised; CE-42..49 filed;
  CE-6, CE-7, CE-46 commented; DEC-34, DEC-35 recorded, DEC-6 amended
- **receipts:**
  - guards: pytest -q: 480 passed in 77.66s (rc=0), lint inside it clean, on main 7ed8c68 plus CE-46
    comment
  - read: orient + task show CE-7, CE-38, ASK-3 + FRAMEWORK §5.5, §6.3, §5.3
  - asked: ASK-3, ASK-4, ASK-5
- **summary** (the owner digest):
  - Owner: DEC-32 (init merges the SessionStart hook into an existing settings file only after
    asking), DEC-33 (ASK-3: criteria rows, one id form, CE-25 split), DEC-34 (every question carries
    a cheap, confident recommendation), DEC-35 (dogfood the whole framework), DEC-6 amended (quick
    adhoc trial; audio-workspace next, CE-43).
  - CE-38 built (bootloader contract, SessionStart hook, G-D0) and adopted in this repo; CE-25 built
    by an ultracode workflow in a worktree: 12 review findings confirmed, 8 fixed, CE-48/CE-49 carry
    the rest.
  - Agent-drafted, owner to read: planned criteria AC-60..64 for US-10, US-12, US-13; goal ids are
    G-n, stamped stories keep G1 (read as G-1).
  - Session scope (owner question): stays per request (DEC-31); the per-task close commit is the
    completion record; G-W11 should derive a dead session's digest (CE-6 log).
  - Found: mid-session commits are red on G-W7 alone (op log committed only at close, CE-45); a
    fast-forward on this machine checks files out CRLF and reddens a kit test (CE-46; Git Bash grep
    cannot see CR).
  - Open for the owner: ASK-5 (rename imported ids with aliases, recommended); restart Claude Code
    after the push (stale MCP server; first live test of the hook).
  - AAR: worktree builds avoid shared-tree collisions but need PYTHONPATH=<wt>/src and
    core.autocrlf=false; the workflow's skeptic pass cut 15 findings to 12 real ones.
- **Still owed:**
  - CE-46 is at LATER with NEXT full: the owner to say whether it swaps with CE-26 or CE-33
  - INV-31 live probes in the first adhoc session (CE-7); the hook's first live run is the owner's
    restart after this push

---

## 2026-10-13a · kind: close

- **rows:** CE-30, CE-31, CE-32, CE-35, CE-36 closed; CE-25 to NOW; CE-33, CE-26 to NEXT; CE-38..41
  filed; ASK-3; CE-6, CE-7, CE-39 commented; US-17; DEC-28..31; DEC-18 amended
- **receipts:**
  - guards: 411 passed in 71.40s (0:01:11); lint: clean
  - read: orient + board + CE-30/31/32/35/36/25 bodies
  - asked: ASK-3
- **summary** (the owner digest):
  - Built, reviewed and closed CE-30 (G-D12 coverage guard), CE-31, CE-32 (decision set), CE-35
    (decision relink), CE-36, as one sequential build -> adversarial review -> fix workflow; every
    reviewer found a real defect
  - Owner re-ranked: NOW CE-25 (design review written; blocked on ASK-3, five calls with
    recommendations), NEXT CE-38, CE-33, CE-26
  - US-17: the framework runs from files it owns; CLAUDE.md becomes a bootloader pointer (CE-38),
    every agent role in the framework (CE-39), framework rules out of the global CLAUDE.md (CE-40)
  - DEC-28 (D-27 imports BUILT, narrowed by D-29), DEC-29 (stale stubs: 3 sessions from last op),
    DEC-30 (ultracode stays a judgement grant; MCP asks for it), DEC-31 (close by default when the
    work is done), DEC-18 amended (fable: arbiter, proofs)
  - Claude Code docs checked into docs/evidence/claude-code-hooks-2026-10-13.md: in-repo @-imports
    load unprompted, SessionStart output reaches context but cannot block, ultracode is also a
    setting
  - AAR: the running MCP server was stale (refused session_start on route key max_bytes), so the CLI
    carried the session; untracked paths need git add before git commit -o
- **Still owed:**
  - push: everything from ab0b155 on is unpushed (owner's call); restart Claude Code so the MCP
    server loads current code

---

## 2026-10-12e · kind: close

- **rows:** CE-10,CE-30,CE-36,CE-37,CE-6
- **receipts:**
  - guards: gate 350 passed (2026-10-13, top level); lint clean
  - read: orient; git log and stats of this session's commits; rituals.md § Clean close and §
    Housekeeping; FRAMEWORK §5.5, §6.1; CE-6, CE-30, CE-36
  - asked: none
- **summary** (the owner digest):
  - Adopted and closed by a later conversation (2026-10-13): this session's conversation was cleared
    after its third commit, leaving its stub open; the owner chose finish-and-close over restart
  - CE-10 closed after a watched green CI run (gate.yml 38266248305 on 058fee7); BTN-3 done
  - Owner picked CE-30 for NOW; its design review written (review: [guard]); CE-36 filed (task close
    warns when NOW would be left empty)
  - US-16 (owner): open sessions are shown to the owner at session start; CE-37 built and closed
    (orient heading, rituals row, AC-52, INV-21)
  - CE-6 comment: the provisional stale-stub rule could not have caught this dead stub; an adopt-
    and-close route belongs beside abandoned in G-W11
  - AAR: a cleared conversation does not end its session; only the owner's question found the open
    stub, which US-16 now puts in front of them
- **Still owed:**
  - push: ab0b155..HEAD (this session's 4 commits plus the close), owner approval needed, then a CI
    watch

---

## 2026-10-12d · kind: close

- **rows:** CE-24,CE-5,CE-14,CE-10,CE-31,CE-32,CE-33,CE-34,CE-35,CE-27
- **receipts:**
  - guards: gate 346 passed (2026-10-12d, top level); lint clean
  - read: orient; workflow result (13 agents); G-D10 and link probes re-run
- **summary** (the owner digest):
  - Owner asked for every NOW and NEXT item done by workflow (ultracode): one sequential run, build
    -> adversarial review -> fix per task, 13 agents
  - Batons: BTN-1 (INV-7 names G-D0) and BTN-2 (refuse reopening an answered ASK, filed CE-31)
    closed
  - CE-24 closed: docs/runbooks/rituals.md holds every ritual's order; runbooks de-leaked and
    shipped in the kit (AC-36, AC-37, INV-13)
  - CE-5 closed: record correct, decision supersede/link/find/show/import, why, generated index;
    G-D6, G-D10 (AC-38..42, INV-14, INV-15); CE-32 filed
  - CE-14 closed: guards.py with G-D1/D2/D3/D7/D8/D9/T3/W7 and [guards] switches (AC-43..51,
    INV-16..20); G-D4/D5 split to CE-33, G-T5 to CE-34, CE-35 filed
  - CE-10 built but open (NOW): .github/workflows/gate.yml; closing needs a push and a watched CI
    run (BTN-3)
  - AAR: reviewer per task paid off: it found real defects in all four (G-D10 laundering, unchecked
    link ids, G-T3 skipping code: links, CI fallback missing); top level re-ran the G-D10 and link
    probes first-hand
- **Still owed:**
  - BTN-3: push + CI watch + close CE-10; NEXT is empty, owner to pick (candidates CE-7, CE-25,
    CE-30)

---

## 2026-10-12c · kind: close

- **rows:** CE-22, CE-20, CE-21 closed; CE-5, CE-14, CE-10 to NEXT; CE-19, CE-13 closed as not
  needed; CE-18 citation note
- **receipts:**
  - guards: pytest -q 278 passed; context-engine lint clean
  - read: orient, task list, census of all open tasks (subagent), diffs of ad3c47f/f0064ff/3048e85,
    config.py::Config.kind_for_id
  - asked: none
- **summary** (the owner digest):
  - Board prioritised with the owner: NOW CE-24; NEXT CE-5, CE-14, CE-10 (CE-22/20/21 done this
    session).
  - CE-22: pause open's commit ends with a Session: trailer; runbook in lockstep (ad3c47f).
  - CE-20: task close refuses an ASK-n; remedy names ask answer / ask later (f0064ff).
  - CE-21: lint G-D0 checks the contract's framework: line and kit marker against the engine's
    major.minor; new [engine] contract key, AC-35 (3048e85).
  - CE-19, CE-13 closed as not needed; CE-18's §12.3 means FRAMEWORK-v0.5.md.
  - AAR: sequential subagents per task worked well for same-file work; subagent actors must be plain
    claude-code/<model> (engine refuses suffixes).
  - Batons: BTN-1 INV-7 register text stale after G-D0; BTN-2 reopen of an answered ASK leaves
    answered:.
- **Still owed:**
  - BTN-1: update INV-7 in REGISTER.md
  - BTN-2: decide reopen-on-answered-ASK behaviour

---

## 2026-10-12b · kind: close

- **rows:** CE-15,CE-16,CE-23,CE-24,CE-6
- **receipts:**
  - guards: gate 259 passed; lint clean (2026-10-12b)
  - read: orient; workflow results; agent reports
  - asked: none (INV prefix asked in chat, answered DEC-27)
- **summary** (the owner digest):
  - CE-15 closed: adoption kit, init (refuses mid-run files), config schema, de-leaked FRAMEWORK;
    design review, 6 residuals INV-7..12
  - CE-16 closed: coverage map docs/evidence/framework-coverage-2026-10-12.md; 6 gap items filed
  - CE-23 closed: design-review gate on promote, residual register on close, G-W12/G-W13; INV-n
    prefix (DEC-27)
  - CE-24 promoted to NOW; DEC-16 amended with owner words on a coordinator-only top level
  - AAR: one workflow (15 agents, plan/build/2-lens review/fix) ran 3 tasks concurrently in one
    tree; commit-by-path held; build agents lacked Agent/Workflow tools so could not sub-delegate;
    concurrent gates went red on each other's uncommitted work
- **Still owed:**
  - kit ships no runbooks (CE-24); no release tag (owner); G-D0 (CE-21)

---

## 2026-10-12a · kind: close

- **rows:** US-15, CE-24, CE-15, CE-22
- **receipts:**
  - guards: pytest -q: 183 passed (2026-10-12a, before close)
  - read: orient + CE-15 + FRAMEWORK §6, §6.11, §7.5, §8.0, §10, §11 + US-11 + charter goals; paste-
    test agent read FRAMEWORK and manual-mode in full
- **summary** (the owner digest):
  - Owner asked if FRAMEWORK.md + manual-mode.md pasted into a repo are enough, and for one source
    of truth for rituals: recorded as US-15.
  - Blind-reader paste test: day-to-day ops work with or without Python; bootstrap, whole rituals by
    hand and housekeeping do not. Evidence: docs/evidence/framework-paste-test-2026-10-12.md.
  - CE-24 (NEXT): rituals runbook, each ritual's steps in one file with engine command and by-hand
    step side by side; FRAMEWORK §6 keeps rules, CLAUDE.md points.
  - Drift fixed: §5.5 key resets on a new day; §6.3 order and CLAUDE.md close carry lint-first and
    pre-close housekeeping; manual-mode hashes (lowercase, no BOM, banner to EOF).
  - Kit gaps (context.toml schema, install, skeletons, adopter gate, repo leaks) on CE-15; pause
    commit trailer on CE-22.
  - AAR: a blind reader given only the shipped files is a cheap, sharp completeness test; worth
    repeating for the CE-15 kit.
- **Still owed:**
  - CE-24 itself (the rituals runbook) is open
  - the hash canonicalisation example in manual-mode (extraction and CRLF shown step by step) is not
    written

---

## 2026-10-11c · kind: close

- **rows:** CE-9 closed; CE-17 commented; DEC-26 new
- **receipts:**
  - guards: pytest 181 passed (includes lint)
  - read: orient + FRAMEWORK.md in full
  - asked: none
- **summary** (the owner digest):
  - DEC-26 (owner): FRAMEWORK.md holds only the framework; history and owner answers archived.
  - FRAMEWORK-v0.5.md: byte-identical archive of the spec before the trim (frozen).
  - FRAMEWORK.md: new Summary and per-section guide; origin story, prior art, dated attributions,
    v0.x markers, §11.3, §12 and §13 removed; section numbers kept; 141 KB to 106 KB.
  - §12 answers not yet in the body were stated in place; rollback and close is new §6.13 (CE-18).
  - Spec route mode: changed in place, no change log. CE-9 closed; CE-17 told to change the spec in
    place.
  - A sonnet audit against v0.5 found no lost rule; it caught two 'Not built yet' misstatements,
    fixed.
  - Push back if: you want build-status notes (*Not built yet*, CE ids) out of FRAMEWORK.md too.
- **Still owed:**
  - nothing

---

## 2026-10-11b · kind: close

- **rows:** CE-4
- **receipts:**
  - guards: pytest -q: 180 passed (lint included)
  - read: CE-4 evidence doc (own, this conversation); tools/sabotage_ce1.py header for conventions
  - asked: none
- **summary** (the owner digest):
  - Owner asked for a tokenizer: tiktoken 0.14.0 installed into the engine env (o200k_base,
    OpenAI's; a proxy, not Claude's).
  - CE-4 baseline gains proxy tokens (§3): S = 14,095 (24,225 with the top item's reading list);
    W-read 14,095 per close, 32,064 with a decision.
  - tools/count_context.py regenerates bytes, lines and proxy tokens at a commit, read-only via git
    show.
  - Bytes per token spans 2.8 to 5.0 across adhoc's docs, so CE-7 reports both; thresholds stay on
    bytes.
  - Exact Claude counts need the token-counting API and a key, which this machine lacks.
- **Still owed:**
  - nothing

---

## 2026-10-11a · kind: close

- **rows:** CE-4, CE-15
- **receipts:**
  - guards: pytest -q: 180 passed (lint included)
  - read: board + CE-4 note + FRAMEWORK §6.1, §6.3, §8.0.3 + DEC-6; adhoc via subagent
  - asked: none
- **summary** (the owner digest):
  - CE-4 closed: adhoc baseline in docs/evidence/adhoc-baseline-2026-10-11.md (adhoc 3e3f442),
    rubric written before the numbers.
  - Session start S = 48,540 B (CLAUDE.md 16,553 + HANDOFF.md 31,987); 78,519 B with today's top
    item's reading list. HANDOFF grew 13% since 2026-10-08.
  - Clean close: W-read 48,540 B every close (114,715 with a decision); W-write median 3,352 B,
    range 1,016-38,816 over 10 write-back commits; 6+2 hand steps.
  - Concurrency incidents recorded in adhoc: none. Bytes only: no tokenizer or API key on this
    machine.
  - Better (for CE-7) = start at least 25% lower, close no higher, no new collisions, no fallback
    reads of the old HANDOFF.
  - CE-15 promoted to NOW (top of NEXT), since NOW must hold one.
  - Delegation: haiku for the clean-tree check, sonnet for the measurement; key numbers re-run
    first-hand, one sum caught and fixed.
- **Still owed:**
  - nothing

---

## 2026-10-10d · kind: close

- **rows:** none
- **receipts:**
  - guards: pytest -q: 180 passed
  - read: CLAUDE.md, .mcp.json, .claude/settings.json, manual-mode.md head
  - asked: none
- **summary** (the owner digest):
  - Owner asked why the MCP server needs CE_PYTHON; recorded DEC-25: if the MCP tools are missing,
    set the server up, fall back to the CLI, ask the owner to restart
  - Tested headless (claude -p haiku): settings.local.json env does NOT reach .mcp.json expansion
    (TOOL_MISSING); env var set: TOOL_OK; local-scope claude mcp add with CE_PYTHON unset: TOOL_OK
  - Registered the server at local scope on the owner's machine; CLAUDE.md Environment and manual-
    mode.md 'When the MCP tools are missing' carry the instruction
  - AAR: test where a setting actually lands before writing it into a ritual; the plausible option
    (settings env) failed
- **Still owed:**
  - nothing

---

## 2026-10-10c · kind: close

- **rows:** CE-3 (closed), CE-4 (promoted to NOW)
- **receipts:**
  - guards: gate green, 179 passed (2026-10-10c); lint clean; tools/sabotage_ce3.py all red
  - read: orient, CE-3, FRAMEWORK 8.0-8.0.3, spike/FINDINGS.md, cli.py, working.py (parts), MCP SDK
    source
- **summary** (the owner digest):
  - CE-3 done: MCP server, one tool per operation in ops.OPS; the CLI now calls the same functions
    (AC-18)
  - Writes one line, reads capped at read_max_bytes=6000 with a pointer (AC-19); AC-18 and AC-19
    tested, 11 sabotage rows red
  - Dogfood VERIFIED headless via .mcp.json + CE_PYTHON, with control; CE_PYTHON is not yet set on
    the owner's machine
  - Agent decision: no SessionStart hook for orient (5195 bytes); session_start must come first
    anyway
  - Agent decision: CE-4 promoted to NOW (first NEXT in the banner); push back if another should
    lead
  - AAR: a PowerShell Set-Content rewrite left a BOM and CRLF in a test file; edit with the Edit
    tool, not shell rewrites
- **Still owed:**
  - Owner: set CE_PYTHON (user env var) so interactive sessions get the MCP tools

---

## 2026-10-10b · kind: close

- **rows:** CE-23
- **receipts:**
  - guards: pytest -q: 139 passed; lint clean (2026-10-10)
  - read: FRAMEWORK P15, P16, 5.2, 7.4; the DfS Regulations PDF; the DfM excerpt
- **summary** (the owner digest):
  - Owner story US-14 recorded verbatim: adopt design for safety (Singapore DfS Regulations 2015)
    and BCA design for maintainability (F.A.M.E.).
  - FRAMEWORK P17 (hierarchy of controls: eliminate, reduce at source, collective, individual;
    residual risks; handover) and P18 (F.A.M.E., BCA text plus meaning here).
  - Task Design review above a threshold (5.2) and invariants as the residual-risk register (7.4)
    designed; build filed as CE-23 at NEXT.
- **Still owed:**
  - session-log header still says keys are minted by hand (carried from 2026-10-09f)

---

## 2026-10-10a · kind: close

- **rows:** CE-10, CE-21, CE-22
- **receipts:**
  - guards: pytest -q: 137 passed (2026-10-10)
  - read: orient; FRAMEWORK 5.4, 5.5, 6.10, 12.3, G-D0; CE-10; DEC-1; DEC-21; context.toml kinds
- **summary** (the owner digest):
  - Owner answers recorded: DEC-22 (ask before every push, push only on green; one task per commit,
    id in the title, Session trailer; repo public), DEC-23 (versioning), DEC-24 (batons).
  - Versioning: engine major.minor = framework version; package now 0.5.0.dev0, contract framework:
    0.5; G-D0 rewritten, build filed as CE-21.
  - CLAUDE.md: push step and a Commits rule per DEC-22; DEC-1 and DEC-13 amended; CE-10 traps
    rewritten for a public repo.
  - FRAMEWORK: G-D0, 6.10, 12.3, new 12.6, a 13 row. Engine pause commit lacks the Session trailer:
    filed CE-22.
- **Still owed:**
  - session-log header still says keys are minted by hand (carried from 2026-10-09f)

---

## 2026-10-09f · kind: close

- **rows:** CE-20, CE-3
- **receipts:**
  - guards: pytest 131 passed (includes lint)
  - read: board only + audit reports + FRAMEWORK diff
  - asked: none
- **summary** (the owner digest):
  - Audited FRAMEWORK.md against the engine and records (two read-only auditors, 49 findings, sample
    re-checked first-hand).
  - Consistency pass applied in place: operation naming rule (lib dotted, CLI noun verb, MCP
    underscores), actors, id prefixes, ledger not a record kind, batons in docs/working, G-R1 and
    schema guards catalogued, §6.9 moved.
  - Where the engine lags the design, dated Built-so-far notes instead of rewriting intent; G-D0
    version schemes open in §12.3.
  - CE-20 filed: engine accepts task close ASK-n. CE-3 comment: pyproject pins mcp>=1.2 vs SDK 2.x.
- **Still owed:**
  - session-log.md preamble still says keys are minted by hand (stale since CE-2)
  - Session: commit trailer (FRAMEWORK §6.10) not required by CLAUDE.md; only 2 of 25 commits carry
    it; owner call

---

## 2026-10-09e · kind: close

- **rows:** DEC-21, US-13, CE-18, CE-19, CE-12
- **receipts:**
  - guards: pytest 131 passed (includes lint)
  - read: board only + FRAMEWORK §12, §6.3-6.4, §6.11, G-W10/G-W11
  - asked: none
- **summary** (the owner digest):
  - Owner answered FRAMEWORK §12.3: Q-F, Q-G, Q-H defaults accepted; Q-J deferred; no housekeeping
    write budget by default (DEC-21).
  - New owner story US-13: rollback-and-close for a session, safe in a shared checkout; filed as
    CE-18 (LATER).
  - Q-J as the owner read it (generated answer-in-place question file) filed as CE-19 (SOMEDAY).
  - FRAMEWORK: new §12.5 table; §12.3 keeps the G-W11 window and rollback-and-close; G-W10 and §6.11
    measure instead of cap; §7.1 Q-H settled.
- **Still owed:**
  - G-W11 stale-stub window still to be measured

---

## 2026-10-09d · kind: close

- **rows:** DEC-18, DEC-19, DEC-20, US-12; FRAMEWORK P16, 6.6, 6.12
- **receipts:**
  - guards: pytest 127 passed 2026-10-09
  - read: FRAMEWORK.md intro/6.6/6.11/13, CLAUDE.md, DEC-17
- **summary** (the owner digest):
  - Recorded owner notes: DEC-18 no fable subagents, DEC-19 keep FRAMEWORK.md current, DEC-20 ritual
    fallbacks (P16), US-12 AAR (first note)
  - FRAMEWORK.md: P16, fable rule in 6.6, new 6.12, three 13 rows; CLAUDE.md Rules updated
- **Still owed:**
  - AAR design (where stored, shape); manual-mode.md has no per-process fallback sections yet

---

## 2026-10-09c · kind: close

- **rows:** CE-15 (comment: DEC-17 ships in the deployed contract)
- **receipts:**
  - guards: gate 123 passed (2026-10-09c)
  - read: CE-15, CE-11, FRAMEWORK §6.6 §6.9 §8.0 §11, DEC-1
- **summary** (the owner digest):
  - Owner rule DEC-17: ultracode has standing approval when it keeps the session's tokens down;
    FRAMEWORK §6.6 and §13.
  - History rewritten (owner): the survey notes and reviews moved out of the repo; every commit SHA
    changed; force-pushed main.
  - Rewrite verified by four independent read-only agents (blobs, metadata, equivalence, residue):
    clean.
  - Answered: how another repo adopts the engine, versioned and upgradable (feeds CE-15; not yet
    written into CE-15).
- **Still owed:**
  - Design draft for CE-15 (versioned install, managed contract blocks, upgrade command) not yet
    recorded

---

## 2026-10-09b · kind: close

- **rows:** CE-15
- **receipts:**
  - guards: pytest -q: 122 passed
  - read: FRAMEWORK P11, §6.6; DEC-15
  - asked: none
- **summary** (the owner digest):
  - DEC-16 recorded verbatim: several tasks in one request -> one subagent per task, top level only
    reports
  - FRAMEWORK P11 and §6.6 carry it as a framework rule; CLAUDE.md § Rules applies it here
  - CE-15 comment: the deploy path must ship DEC-16
- **Still owed:**
  - nothing

---

## 2026-10-09a · kind: close

- **rows:** CE-3
- **receipts:**
  - guards: gate pytest -q green, 121 passed (2026-10-09)
  - read: CLAUDE.md, ce orient, FRAMEWORK §8.0.2, HANDOFF
  - asked: none
- **summary** (the owner digest):
  - Owner chose one name, context-engine, for the CLI and the MCP server; tool names use underscores
    (DEC-15, PROVISIONAL)
  - Renamed ce -> context-engine in pyproject's script entry, cli.py prog, refusal remedies,
    CLAUDE.md, the runbook, context.toml routes, criteria; older records keep ce
  - Fixed a clock-dependent assertion in tests/test_working.py (AC-25): main() fills decided from
    the real clock, so it went red once the date passed 2026-10-08
  - Sabotage: runbook heading reverted to ce -> test_runbook red; record-new date fill forced to
    2000-01-01 -> AC-25 test red
- **Still owed:**
  - nothing

---

## 2026-10-08f · kind: close

- **rows:** CE-8 (closed); CE-3 (NEXT -> NOW); CE-15 (LATER -> NEXT); DEC-1..13, US-1..11 (stamped);
  DEC-7 (amended); AC-22, AC-23, AC-24, AC-25 (tested)
- **receipts:**
  - guards: gate 120 passed; ce lint clean; tools/sabotage_ce8.py 11/11 red
  - read: HANDOFF banner and start-here, CE-8 task, cli.py, store.py, working.py, config.py,
    context.toml, manual-mode.md (append-only and lint sections), CLAUDE.md
  - asked: none
- **summary** (the owner digest):
  - CE-8 is done: this repo now runs its own framework through the engine, not by hand.
  - New commands: ce record new/stamp/amend for decisions and stories, ce routes for the routing
    table.
  - All 24 decisions and stories are stamped; ce lint is clean and is now part of the gate.
  - The routing table moved from CLAUDE.md into context.toml; lint fails if a routed path
    disappears.
  - CLAUDE.md rituals are now ce commands; the manual-mode runbook is the fallback when ce errors.
  - Every new guard was sabotaged: 11 rows in tools/sabotage_ce8.py, all red. NOW is CE-3 (MCP
    server).
- **Still owed:**
  - CE-3 next: the MCP server over these same Engine functions (AC-18, AC-19)
  - tools/sabotage_ce2.py may not match on CRLF checkouts (HANDOFF fact, 2026-10-08f)

---

## 2026-10-08e · kind: close

- **rows:** CE-8 (manual-mode runbook; touched); US-11 (created, amended); AC-21 (tested);
  okf._section_span (bug fixed); context.toml (question labels type); CLAUDE.md (routing row:
  runbooks)
- **receipts:**
  - guards: gate pytest -q green, 115 passed (2026-10-08e); sabotage 4 of 4 red (runbook section,
    Why line, new subcommand, section regex); ce lint: 24 failures, all G-D10 no body_sha (stamping
    is CE-8)
  - read: orient banner; CE-8 task; src/context_engine cli, working, store, ledger, okf, config;
    context.toml; FRAMEWORK 5.5, 7.5; subagent audit of the runbook against the code
  - asked: none open
- **summary** (the owner digest):
  - Owner: rituals must work without Python, each with its reason (US-11, plus an amendment).
  - Wrote docs/runbooks/manual-mode.md: every ce operation as by-hand steps with a Why; it is the
    reference when the engine errors.
  - AC-21: the gate fails if a ce subcommand has no runbook section or a section has no Why;
    sabotaged red 3 ways.
  - An audit of the runbook against the code found 14 mismatches and 8 gaps; all fixed in the text.
  - One was an engine bug: section lookup matched by prefix (## Logs, ## Read first). Fixed test-
    first.
  - Next in CE-8: stamp bodies, add ce stamp/amend, routing to context.toml, CLAUDE.md rituals as ce
    commands.
- **Still owed:**
  - push and its CI watcher: done after this entry, see the commit

---

## 2026-10-08d · kind: close

- **rows:** CE-2 (closed); CE-8 (NOW, Traps and Read first written); CE-6 (comment: G-W11); AC-10 to
  AC-17 (tested); DEC-14 (created); CE-1, ASK-1, ASK-2 (status: deprecated, G-W4); CLAUDE.md §
  Sabotage rule (fresh bytecode cache)
- **receipts:**
  - guards: gate pytest -q green, 112 passed (2026-10-08d); sabotage tools/sabotage_ce2.py 34 of 34
    red; ce lint: 23 failures, all G-D10 no body_sha (stamping is CE-8)
  - read: board + CE-2 and its Read first; FRAMEWORK §5.2 to §5.5, §6.1, §6.3, §6.4, §7.1, §8.0.1,
    §8.0.2, §8.4; zanzibar check_session_receipt, BANNER_MAX_LINES, check_read_first
  - asked: none open
- **summary** (the owner digest):
  - Built CE-2: the ce CLI (python -m context_engine) runs sessions, the board, owner questions,
    batons, pauses, the banner, orient and lint.
  - Session keys are minted under the lock with a kind: open stub; close refuses a bad receipt or an
    unraised NEXT or overdue question.
  - This session was opened, closed and bannered through the engine itself; its first writes changed
    only their own lines.
  - Agent calls in DEC-14: one ledger file under the lock (Q-H), BTN/PAU record kinds, orient capped
    at 6000 B (this repo measures 3015 B).
  - Sabotage caught its own harness: a same-length edit ran stale bytecode and passed green. Fixed
    with a fresh cache per run; rule in CLAUDE.md.
  - Next is CE-8: stamp this repo's bodies and rewrite CLAUDE.md's rituals as ce commands.
- **Still owed:**
  - G-W11 (stale-stub window, abandoned stubs) moved to CE-6
  - push and its CI watcher: done after this entry, see the commit

---

## 2026-10-08c · kind: close

- **rows:** CE-1 (closed); CE-2 (NOW); AC-1 to AC-9 (tested); DEC-10 to DEC-12 (status ACCEPTED
  corrected to BUILT, the spec's vocabulary); ASK-2 (closed); DEC-13 (created); CE-5, CE-8
  (deps); FRAMEWORK §6.5 and Q-I
- **receipts:**
  - guards: gate `pytest -q` green, 72 passed (2026-10-08); sabotage `tools/sabotage_ce1.py`
    13 of 13 red; engine `lint` on this repo clean except "no body_sha" (stamping is CE-8)
  - read: CE-1 and its Read first; FRAMEWORK §8.0 to §8.0.2, §8.3, §9.3, §9.3.1
  - asked: ASK-2 answered by the owner (DEC-13)
- **summary** (the owner digest):
  - Built the engine core (CE-1): OKF records, ids under a cross-process lock, op log,
    write-time refusal, lint for schema, G-D10 and G-D11. Library only; the CLI is CE-2.
  - Writes are surgical: ruamel re-dumps 14 of this repo's records differently, so only changed
    keys are re-serialised. The first real writes (CE-1, CE-2) touched only their own lines.
  - Sabotage caught a test that could not fail (AC-7: `parse` normalised before the hash did);
    the test now hashes raw CRLF. The concurrency test caught a mkdir race; fixed.
  - The new schema check caught DEC-10 to DEC-12 using `ACCEPTED`, outside the spec's vocabulary.
  - ASK-2: corrections are insert-only `[brackets]` (DEC-13). CE-8 now follows CE-2 (CLI first).
    Pushed `bd22aa1` (owner: push freely while there is no CI; watcher: no runs).
- **Still owed:**
  - nothing

---

## 2026-10-08b · kind: close

- **rows:** ASK-1 (closed); US-9, US-10, DEC-10 to DEC-12, CE-14 to CE-17 (created); DEC-6
  (amended); CE-7 (deps += CE-8); FRAMEWORK P15 added
- **receipts:**
  - guards: none exist yet; gate not run (docs and records only, no `src/` or `tests/` change)
  - read: HANDOFF in full; ASK-1, ASK-2, charter; FRAMEWORK §5.5, §8.0, §8.0.1, §10, §11.1,
    §11.2; CE-2, CE-7, CE-8, DEC-6
  - asked: ASK-1, ASK-2 raised; ASK-1 answered, ASK-2 still open
- **summary** (the owner digest):
  - Owner confirmed the charter and widened it: the goal is the whole FRAMEWORK.md, deployable
    across all repos, not only the engine (new G7). A server the owner manages is an anti-goal.
  - Order: dogfood here first (CE-8), then work out adoption (CE-15), then the adhoc trial.
  - Filed the gaps the engine-only board missed: guard catalogue (CE-14), deploy path (CE-15),
    and a coverage map of the whole spec (CE-16, NEXT) to find the rest.
  - Sabotage rule made an owner mandate (DEC-11): charter, `CLAUDE.md`, criteria statuses.
  - Owner asked for tiled tests keyed on a code hash (US-10): G-V1 has the hash part; tiles,
    per-tile input hashes and showing it at session start are filed as CE-17.
  - New spec principle P15, design for an agent that starts with no context (DEC-12).
  - Fact: Remote Control spawns default to `same-dir` (owner screenshot), matching §5.5.
- **Still owed:**
  - pushes: commits `0964993` onward are local only (no permission asked)
  - ASK-2 unanswered (blocks CE-5)

---

## 2026-10-08a · kind: close

- **rows:** CE-1 to CE-13, ASK-1, ASK-2 (all created); US-1 to US-8; DEC-1 to DEC-9; AC-1 to AC-20
- **receipts:**
  - guards: none exist yet (the engine is the guard package); gate `pytest -q` green, 1 test
  - read: n/a, the founding session (it ran from `PycharmProjects/.scratch`)
  - asked: ASK-1, ASK-2 raised in chat at close
- **summary** (the owner digest):
  - Explained the framework; with the owner, designed v0.5 (the record engine, MCP,
    housekeeping, decisions as OKF records) and read the OKF v0.2 spec for it.
  - Created this repo (private, `averykhoo/context-engine`), env `context-engine` (Python
    3.12), and moved the framework spec in, tracked (DEC-1 to DEC-3).
  - Step-0 spike: `.mcp.json` `${VAR}` expansion, subagents sharing the server, SessionStart
    hook injection and shutdown at session end all verified with controls; `/clear` not.
  - Agent decisions to push back on: adhoc as the first trial (DEC-6, PROVISIONAL); the id
    prefixes and manual mode (DEC-7); SDK 2.x and ruamel (DEC-8).
  - 20 criteria drafted (all `planned`); charter reconstructed and `unconfirmed` (ASK-1).
- **Still owed:**
  - pushes: commit `1975e5a` was pushed (CI watcher: no workflows, 0 runs); the founding
    commit of this ledger and the board is local only, unpushed (no permission asked)
  - the framework's own guards do not exist, so nothing checks these records yet (CE-8)
