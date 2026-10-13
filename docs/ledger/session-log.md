# Session ledger

Append-only, newest first, one entry per session without exception (FRAMEWORK §7.1). Kinds:
`close`, `pause`, `foreign` (human commits reconciled), and, once the engine mints keys, `open`
and `abandoned`. Until then (DEC-7) the session key is minted by hand at write-back as
`max(newest key here, HANDOFF banner key) + 1 letter`.

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
