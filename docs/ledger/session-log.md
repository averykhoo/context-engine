# Session ledger

Append-only, newest first, one entry per session without exception (FRAMEWORK §7.1). Kinds:
`close`, `pause`, `foreign` (human commits reconciled), and, once the engine mints keys, `open`
and `abandoned`. Until then (DEC-7) the session key is minted by hand at write-back as
`max(newest key here, HANDOFF banner key) + 1 letter`.

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
