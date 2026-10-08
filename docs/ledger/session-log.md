# Session ledger

Append-only, newest first, one entry per session without exception (FRAMEWORK §7.1). Kinds:
`close`, `pause`, `foreign` (human commits reconciled), and, once the engine mints keys, `open`
and `abandoned`. Until then (DEC-7) the session key is minted by hand at write-back as
`max(newest key here, HANDOFF banner key) + 1 letter`.

---

## 2026-10-08b · kind: close

- **rows:** ASK-1 (closed); US-9, DEC-10, DEC-11, US-10, CE-14, CE-15, CE-16, CE-17 (created); DEC-6 (amended);
  CE-7 (deps += CE-8)
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
