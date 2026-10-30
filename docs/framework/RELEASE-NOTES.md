# Framework release notes

LIVING. What changed in the framework, version by version, for a repo that has adopted it: read
the notes from your pinned version on before moving the engine's pin (FRAMEWORK §8.0, upgrade
procedure). Each line says what changed, the FRAMEWORK section that now holds the rule, and the
decision (`DEC-n`) or, where no decision was recorded, the engine task (`CE-n`) that says why;
both are in this repo (`context-engine why <id>`, `context-engine task show <id>`). Newest
first. A version's notes are added on top; an earlier version's notes are not rewritten. Build
status is not here: it is on the board.

## 0.5, from 2026-10-30: changes since the cut

- G-D3 also checks the backticked file names and repo paths in the docs a new `[guards] paths`
  list names (the kit ships it empty: off), and fails a bare file name that matches several
  files whose texts differ (§8.3) — DEC-113, DEC-114.
- The roster: every role the session delegates, with what it runs as, its model tier, what it
  writes and what it returns, the arbiter on `fable` where the owner asked for it; the kit
  ships the roster as text, not as named agents (§6.6) — DEC-18, CE-39.
- A replaced reconstruction is confirmed by asking the owner again, never by quoting their
  earlier confirmation; `record confirm` refuses the words that confirmed a story the successor
  replaces (§3.2) — DEC-66, CE-102.

## 0.5, 2026-10-23: FRAMEWORK.md cut to what a user needs (CE-93)

**No existing rule changed; one was added** (these release notes, the last line below). The
text was cut to what is needed to understand and use the framework (DEC-49); the text before the
cut is `FRAMEWORK-v0.5-2026-10-23.md`, beside FRAMEWORK.md.
- Every *Not built yet* and *Built so far* marker, and every `(CE-n)`, is gone: build status is
  on the engine's board. A part that a repo adds when it needs it says so through §11.2's
  trigger instead (the deviation register, G-T4, the G-V2 raw-total floors).
- How the engine carries out a rule moved to `docs/engine.md`: how a commit is built when other
  sessions' op lines stay out, the cases where the engine cannot commit, the foreign-commit
  ranges under a rebase, the run ledger's ids, the lock's timeout. `manual-mode.md` already held
  the by-hand form of each.
- Operation detail the runbook already holds was cut to a pointer: what `record retire`,
  `record confirm`, `decision set` and `decision import` check and refuse, case by case.
- Dated incidents, probe notes and regulation clause numbers were cut; the archived copy holds
  them until incidents are records of their own (DEC-47, CE-94).
- §8.3 G-D3 now says what lint does since CE-41: a bare file name resolves to a file git does not
  ignore (CE-89 item 1).
- §6.12 and §8.0 add these release notes, and the upgrade procedure now starts by reading them.

## 0.5, 2026-10-11 to 2026-10-23: rules changed since `FRAMEWORK-v0.5.md` (2026-10-10)

**Who decides and how sessions work**
- Who decides is set by reversibility first: a call cheap to undo is the agent's, recorded
  PROVISIONAL and flagged in the digest (P8, §5.3) — DEC-48.
- The top-level session coordinates: every task, even one, goes to a subagent; checks and
  verification go to agents (§6.6, P11, the contract) — DEC-44, DEC-60, CE-83.
- Ultracode needs no per-request opt-in when it keeps the session's context down; the grant
  lives in the contract (§6.6) — DEC-30.
- A session closes eagerly when its requested work is done (§6.3, the contract) — DEC-31, CE-82.
- Every owner question carries a recommendation when one is cheap to reach (§5.3) — DEC-34.
- "Rituals" are called procedures everywhere (§6) — DEC-39, CE-68.

**Session start, close and the board**
- Session start shows the owner the other open sessions, each with when it last did anything
  (§6.1 item 3) — CE-37, CE-104.
- Clean close step 7 runs lint and `gate status` instead of a second full gate run, and re-runs
  only the scope's readers (§6.3 item 7) — DEC-49 (dedupe-1), CE-92.
- Ranking runs at two cadences: a light reorder at every close, and the full re-rank (§6.14)
  when NEXT holds no task; every open task names its charter goals (§5.2, G-I1) — DEC-64,
  DEC-68, CE-99.
- Closing the NOW item while others stay open says G-W5 is red and asks the owner which item to
  promote (§5.2) — CE-36.
- An owner question closes only through `ask answer`, and an answered question never reopens
  (§5.3) — CE-20, CE-31.
- A delegated ruling ("you decide") is recorded as `actor: owner asked` with `ruled_by` and a
  `## Ruling` section, never as the owner's words; lint G-I3 (§6.5, §8.1) — CE-113.
- A stale session stub is abandoned by `session abandon --stale`, run by start-of-session
  housekeeping after 3 later sessions counted from its last activity (§7.1, G-W11) — DEC-29,
  DEC-69, CE-124.
- Foreign commits are reconciled from the previous session's start head, not the newest ledger
  commit (§6.10 item 2) — CE-65.

**Commits**
- The engine commits its own writes by path, at milestones; every other write goes into the next
  commit (§5.5 rule 4) — DEC-36, CE-45, CE-55.
- A commit takes only the committing session's op lines, plus a line naming a file it carries;
  `--sweep` takes every line (§5.5 rule 4) — CE-125.
- The session's own commits go through `context-engine commit`, which lints what it carries and
  refuses a code path no green gate run covers (§5.5 rule 4, §8.5 G-V1) — CE-55, CE-63, CE-78.
- Agent commits end in one trailer paragraph holding `Session:` and every other trailer (§6.10
  item 1) — DEC-22, CE-64.
- Prose writes (`banner set`, the ledger entry) refuse what lint would fail (§5.5 rule 2) — CE-63.

**Intent records**
- One id form for every id a repo mints, `[A-Z]+-[1-9][0-9]*`; goals are `G-n` (P3) — DEC-33,
  DEC-38.
- Criteria are rows; a criterion's actor is its source's; the chain's guards G-I1, G-I2, G-T1,
  G-T2, G-T6 read the sources `[guards]` names (§3.3, §8.1) — DEC-33, CE-25.
- A story is retired only by `record retire`, and a reconstruction is confirmed only by `record
  confirm` with the owner's words; a replaced reconstruction is confirmed by asking again (§3.2,
  G-I2) — CE-49, CE-58, DEC-66.
- `decision set` and `decision relink` own a decision's own keys and its code links (§6.5) —
  CE-32, CE-35.
- `decision import` keeps every number, renames an id in another prefix keeping the old one as an
  alias, and never loses text silently; an entry with no recorded actor imports as `unrecorded`
  (§6.5, §11.4) — DEC-37, DEC-40, DEC-57, CE-74, CE-98.

**Docs, guards and the gate**
- Docs declare their liveness (G-D4) and typed counts are red outside P5's forms (G-D5) — CE-33.
- Every component, procedure and G-id FRAMEWORK names is owned by a coverage map or a board item
  (G-D12) — CE-30.
- `doc freeze` and `doc archive`; a close refuses while an ACTIVE-PLAN doc it ends is unfrozen
  (§6.7, §7.2, §7.3) — CE-27.
- The scoped gate: each run is recorded against its scopes' content ids, and the code gate runs
  only when the code changed (§8.5 G-V1, §11.1) — CE-78.
- The design review above a threshold, and the residual-risk register with `INV-n` ids (P17,
  P18, §5.2, §7.4, G-W12, G-W13) — DEC-27, CE-23.
- Where CI runs on another platform, its job is also run locally before a push (§6.8) — CE-67.

**Adoption**
- `CLAUDE.md` carries only the kit block, which imports the framework's own contract; a
  `SessionStart` hook in the machine-local settings runs `orient`, merged into an existing file
  only with the owner's yes (§6.9) — DEC-32, CE-38.
- The engine is a pinned, non-editable install in `.context-engine/env/` inside the target repo,
  gitignored (§6.9 step 2) — DEC-41, CE-81.
- The method runbooks (`gate.md`, `sabotage.md`, `fan-out.md`, `release.md`) ship in the kit
  with `procedures.md` and `manual-mode.md` (§7.5) — CE-24, CE-26.
- The engine's Claude Code plugin: a skill per procedure that points at its runbook section
  (§7.5, §11.2) — CE-77.
