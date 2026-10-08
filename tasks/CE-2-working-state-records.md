---
type: Task
id: CE-2
title: "Working state: tasks, questions, batons, pauses, ledger; session ops; orient; lint"
brief: "Session key minted at start under the lock with a kind: open stub; closing never moves a file"
pri: NOW
state: open
deps: [CE-1]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08c
updated: 2026-10-08c
closed:
---

Build step 2: the working-state record kinds and the session rituals as operations, CLI
first. Claims AC-10 to AC-17. Operations: `session start | close | pause`, `orient`; task
`new | set | promote | dep | comment | touch | close | reopen | list | show`; `ask new | raised |
later | answer`; `baton add | done`; `pause open | resume`; `banner set`; `lint`.

## Traps

- **Q-H is an agent call made here** (FRAMEWORK §12.3): the ledger as one file per entry, or one
  file under the lock. Default: one file under the lock. Record the choice as a DEC.
- The stale-stub window (G-W11) needs a value with provenance (G-D9): measure it, never copy
  an example.
- `orient()` needs a hard size cap (AC-17); set it by measuring this repo's own output, and
  record how.
- This repo's `tasks/`, `docs/ledger/session-log.md` and `HANDOFF.md` are the first fixtures
  and the first users (CE-8).

## Read first

- `docs/framework/FRAMEWORK.md` §5.2–5.5, §6.1, §6.3, §6.4, §7.1, §8.4
- `docs/criteria.md` § Working state
- zanzibar `scripts/handoff_lint.py::check_session_receipt`, `::MAX_LINES`;
  `scripts/task.py::BANNER_MAX_LINES`, `::check_read_first`, `::check_min_parsed`;
  `docs/tasktool-trial-protocol.md`

## Log
