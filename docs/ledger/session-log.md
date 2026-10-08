# Session ledger

Append-only, newest first, one entry per session without exception (FRAMEWORK §7.1). Kinds:
`close`, `pause`, `foreign` (human commits reconciled), and, once the engine mints keys, `open`
and `abandoned`. Until then (DEC-7) the session key is minted by hand at write-back as
`max(newest key here, HANDOFF banner key) + 1 letter`.

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
