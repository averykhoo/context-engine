---
type: Runbook
title: "Manual mode: every engine operation done by hand, and why each step exists"
source: US-11
created: 2026-10-08
---

# Manual mode

Every operation the engine (`ce`, `python -m context_engine`) performs, written as steps a person
or an agent can follow with a text editor, git and a SHA-256 tool. It exists for two reasons
(US-11):

1. **Fallback.** A repo with no Python can still run the framework: slowly, by hand, with the
   same files and the same rules.
2. **Reference behaviour.** Each step says **why** it exists. When the engine errors, refuses
   oddly or writes something that looks wrong, this is the statement of what the right result
   was, so the agent can finish the job by hand *and* fix the engine.

A guard keeps it whole: `tests/test_runbook.py` fails the gate if any `ce` subcommand has no
`### ce <group> <op>` section here, or a section has no **Why** (AC-21).

## When the engine and this runbook disagree

- **A refusal is not a bug.** Refusals are the engine doing its job: every one prints a remedy.
  Do what the remedy says. Only treat a refusal as a bug when the Why below says the write should
  have been allowed.
- **The engine is wrong** (it wrote what this runbook says it must not, or refused what it must
  allow): finish the step by hand from this runbook, then fix the engine with a test that fails
  first (sabotage rule, DEC-11), and name the step here in the commit message.
- **This runbook is wrong** (the engine is right and the text is stale): fix the text in the same
  commit as the code it describes. The Why is the tiebreaker: whichever side serves it wins.
- **Neither is clearly right:** it is a decision. Record it (`DEC-n`), or ask the owner if it
  changes what they asked for.

## What every write does

These hold for every operation below. The per-operation sections only list what is extra.

| Rule | By hand | Why |
|---|---|---|
| **Take the lock** | No lock exists by hand. Instead: re-read the file immediately before editing it, and run `git status` and `git log -3` before committing. | Several sessions share one checkout. The engine's OS lock stops two writers losing each other's change (AC-9); by hand, re-reading is the only defence. |
| **Check the caller** | Know your session key (like `2026-10-08e`) and your actor (`human:<id>`, `process:<id>`, or `<producer>/<version>` such as `claude-code/<model-id>`). Every write below records them. | Each write has to say which session made it and who did it. Without that, nobody can find a change or trace it back (OKF §7). |
| **Validate before writing** | Check the result against its kind's schema (table below). If it fails, do not save it. | A bad record that reaches disk breaks every later reader. The engine checks before writing any byte (AC-5). |
| **Change only your own lines** | Edit only the frontmatter keys the operation names. Keep every other line exactly as it was: order, quoting, comments, unknown keys. Keep the file's line endings. | Byte-stable writes keep diffs reviewable and keep keys that other tools own (AC-1, AC-2). |
| **YAML shapes** | Lists in flow style: `deps: [CE-2, CE-3]`. Dates unquoted: `created: 2026-10-08`. Null is the bare key: `closed:`. Quote any value with `: ` in it. | Quoted dates fail the `date` type, and an unquoted colon broke DEC-6 once (`CLAUDE.md` § Gate). |
| **New keys go last** | A key the record does not have yet (`status`, `closed`, `answered`, `done`, `evidence`, `resumed`, `expired_to`, `body_sha`) is added after the last key. An existing key is replaced where it stands, keeping an end-of-line comment. | Keeps every untouched line in place, so the diff shows only the change. |
| **New records** | Frontmatter, the closing `---`, one blank line, the body, one final newline. `deps: []` is written even when empty. | One shape for every record keeps hand-written and engine-written files identical. |
| **Bump `updated`** | On every write to a board item (task or question), set `updated: <session key>`. | It is how a reader sees a record was touched this session without reading the op log. |
| **Log the operation** | Append one line to `docs/ledger/ops.jsonl` (format below). | The op log is the audit trail: who changed which keys, in which session (AC-6). G-W7 will read it. |
| **Engine-owned keys** | Never hand-edit `type`, `id` or `body_sha` on an existing record. | Ids are never reused or renumbered (P3). `body_sha` pins an owner's words (G-D10). |

**Op log line**, one JSON object per line, UTF-8, `\n` endings:

```json
{"at": "2026-10-08T18:10:28+08:00", "session": "2026-10-08e", "actor": "claude-code/<model-id>", "op": "close", "id": "CE-8", "path": "tasks/CE-8-dogfood-adoption.md", "fields": ["state", "status", "closed", "moved", "updated", "body"], "mechanical": false}
```

`at` is local time with its offset. `fields` lists the keys changed, plus `"body"` if the body
changed. `mechanical` is `true` only for housekeeping and the `--mechanical` flag.

| Operation | `op` | `id`, `path` | `fields` |
|---|---|---|---|
| any new record (task, question, decision, baton, pause) | `new` | the record | every frontmatter key, `type`, `id` and `body_sha` included |
| task set, promote, dep, comment, touch, close, reopen, section | `set`, `promote`, `dep`, `comment`, `touch`, `close`, `reopen`, `section` | the item | the changed keys, then `updated`, then `body` if the body changed |
| ask raised | `ask.raised` | one line per question, then one with id = session key, path = the ledger | `["last_asked", "updated"]`; the ledger line `["asked"]` |
| ask later, ask answer | `ask.later`, `ask.answer` (answer also writes a `new` line for its `DEC-n`) | the question | the changed keys, `updated`, `body` |
| baton done, pause resume | `baton.done`, `pause.resume` | the record | the changed keys |
| baton expire | `new` then `hk.expire_batons`, both mechanical | the task, then the baton or pause | as above |
| session start, close, pause | `session.start`, `session.close`, `session.pause` | id = session key, path = the ledger | `["kind"]` |
| banner set | `banner.set` | id = session key, path = `HANDOFF.md` | `["banner"]` |
| record stamp, record amend | `stamp` (one line per id), `amend` | the record | `["body_sha"]`; `[]` |

### Record kinds here (from `context.toml`)

| Kind | Id | Directory | Mode | Required keys | Enums and types |
|---|---|---|---|---|---|
| decision | `DEC-n` | `docs/decisions` | append-only | title, actor, decided, session, decision_status | decision_status: BUILT, PROVISIONAL, DEFERRED, SUPERSEDED, REJECTED; decided date; session key |
| story | `US-n` | `docs/stories` | append-only | title, actor, date, story_status, goals | story_status: live, unspecified, unconfirmed, retired; date date; goals list |
| task | `CE-n` | `tasks` | replaced | title, pri, state, created | pri: NOW, NEXT, LATER, SOMEDAY; state: open, closed; created date; moved, updated, closed keys; deps, labels lists |
| question | `ASK-n` | `tasks` | replaced | title, pri, state, created | as task, plus blocks list, last_asked key |
| baton | `BTN-n` | `docs/working` | stamped | title, session, state, created | state: open, done, expired; session, done keys; created date |
| pause | `PAU-n` | `docs/working` | stamped | title, session, state, created, branch, resume_step | state: open, done, expired; session, resumed keys; created date; uncommitted, deferred lists |

Every record also has `type:` (Decision, Story, Task, Question, Baton, Pause) and `id:` matching
its file name. OKF `status`, if present, is `draft`, `stable` or `deprecated`; record states use
their own keys (`state`, `decision_status`, `story_status`) because OKF reserves `status`.

### Session keys

A key is `YYYY-MM-DD` plus letters: `a` to `z`, then `aa`, `ab`, and so on. Keys sort by date,
then by letter count, then alphabetically, so `z` comes before `aa`.

### The two hashes

- **Body hash (`body_sha`)**, for append-only records: take the body (everything after the
  frontmatter's closing `---` line). Cut it at the first line that is exactly `## Amendments`
  (trailing spaces allowed) if there is one. Convert CRLF to LF, strip leading and trailing
  newline characters (only `\n`: a line of spaces stays in), and add one `\n`. Then
  `sha256:` + the full hex SHA-256 of those UTF-8 bytes. *Why: it makes "verbatim" checkable.
  Rewriting an owner's words changes the hash (G-D10), and amendments sit below the cut so they
  never break it.*
- **Banner hash**: take the `## Banner (<key>)` heading line through to the next `## ` heading.
  Convert to LF and strip leading and trailing `\n` characters. Then `sha256:` + the **first 16** hex
  characters. *Why: `banner set` must refuse when another session rewrote the banner since you
  read it (FRAMEWORK §5.5 rule 2).*

By hand: `printf '%s\n' "$text" | sha256sum` (Git Bash), or
`Get-FileHash -Algorithm SHA256` on a file holding exactly the canonical bytes (PowerShell).

---

## Sessions

### ce session start

1. Read the newest key in `docs/ledger/session-log.md`. Entries are `## <key> · kind: <kind>`,
   newest first. Also read the banner key in `HANDOFF.md`'s `## Banner (<key>)`.
2. Take the larger of the two. If it is from an earlier day than today, the new key is today's
   date + `a`. Otherwise it is that key + 1 letter.
3. Insert a stub as the **first** entry, straight after the preamble's `---` line, followed by
   its own `---` separator:

   ```
   ## 2026-10-08e · kind: open

   - **opened:** 2026-10-08T19:02:11+08:00 by claude-code/<model-id>
   ```
4. Commit the ledger by path promptly. The engine leaves this commit to you.

`HANDOFF.md` may be missing, but if it exists it must have a `## Banner (<key>)` heading:
without one, session start, orient and both banner commands refuse.

The engine re-renders the whole ledger on every write: the preamble ends in a `---` line, entries
are separated by a blank line, `---` and a blank line, and the last entry has no `---` after it.
Match that by hand.

**Why:** two sessions minting a key at the same time could otherwise collide. The stub reserves
the key the moment it is minted, shows the session is live (`orient` lists open stubs), and
leaves evidence if the session dies (G-W11) (FRAMEWORK §5.5 rule 1, AC-10). The banner key
counts too, because a session may have written the banner before its ledger entry.

### ce session close

1. Your stub must exist and still say `kind: open`. A session closes or pauses once.
2. You need: `rows` (the items you touched, not empty); a summary of 1 to 7 lines (the owner
   digest); a `guards` receipt (gate and lint results, verbatim); a `read` receipt (what you read
   to start work). `asked` and `Still owed` are optional; an empty `Still owed` is written as
   `nothing`.
3. Check the asked ids: the ids in your `asked` text **plus** those in the stub's `- **asked:**`
   line (written by `ask raised`). Together they must name every open owner question at NOW or
   NEXT, and every overdue one. A question is overdue if `last_asked` is empty, or at least 5
   closes/pauses have happened since it, or it is at least 7 days old. The receipt written is your
   `asked` text if you gave one, otherwise the stub's line.
4. Replace the stub's text, keeping its position, with (bullets wrapped at 100 columns,
   continuation lines indented):

   ```
   ## <key> · kind: close

   - **rows:** CE-8 (runbook written); US-11 (amended)
   - **receipts:**
     - guards: gate pytest -q green, N passed; ce lint: ...
     - read: ...
     - asked: none open
   - **summary** (the owner digest):
     - one line per point, 1 to 7 of them
   - **Still owed:**
     - nothing
   ```
   Leave out the `asked:` line if it is empty. Op log: `session.close`, fields `["kind"]`.

**Why:** the close is what the next session trusts. The receipts prove the gate ran and say
what was read. The asked check stops owner questions going unraised for days (G-W6, G-W8,
AC-11). The 7-line cap keeps the digest something the owner will actually read (FRAMEWORK §5.6).

### ce session pause

1. As for close step 1. You need `rows` and `deferred` (the steps skipped: gate, commit, ...).
2. Replace the stub with:

   ```
   ## <key> · kind: pause

   - **rows:** ...
   - **deferred:** ...
   ```

**Why:** a session interrupted mid-work still leaves a ledger entry (one per session, no
exceptions, FRAMEWORK §7.1). More than 2 pauses in a row without a close fails G-W2, because
skipped gates and commits pile up.

## Reading

### ce orient

Read and report, in this order, in under 6000 bytes in total (`orient_max_bytes`). If a part does
not fit, cut it at a line and say where the rest is:

1. the banner (`HANDOFF.md` § Banner);
2. open batons and pauses (`docs/working/`, `state: open`), your own session's first, each pause
   with its resume step and branch;
3. other sessions with an open stub in the ledger;
4. board items at NOW and NEXT (as `ce task list`);
5. owner questions to raise now: open at NOW or NEXT, or overdue (see session close step 3);
6. the NOW item's brief, `## Traps` and `## Read first`.

**Why:** one bounded read at session start replaces opening a dozen files (US-1, AC-17). The
order is the order of urgency: carried work and live sessions come before new work.

### ce routes

Read the `[[routes]]` entries in `context.toml`, in order. Each names a component, its path
(plus `pattern`, how files under it are named), its change `mode`, and an optional `note`.

**Why:** before writing anything, know where it belongs and whether it may be edited, replaced,
or only appended to. The table used to sit in `CLAUDE.md`; it lives in config now so the engine
can check it (G-R1) and every repo can carry its own (FRAMEWORK §2).

### ce lint

Check every record, then the working state. `--working` does only the second half.

- **schema**: every record in a kind's directory whose name starts with its id parses (valid
  YAML, a closing `---`), has the right `type` and `id`, every required key, enum values in
  range, values of the declared type, and an OKF `status` from draft/stable/deprecated.
- **G-D10**: every append-only record (decision, story) has `body_sha`, and it matches the body
  hash above. *Why: owner words are verbatim, so a rewrite must show up.*
- **G-D11**: every `.md` in a bundle directory (`docs/decisions`, `docs/stories`, `tasks`, and
  each kind's directory), subdirectories included, parses and has frontmatter with a `type`. The exceptions are `log.md` and
  `index.md`, and `index.md` may carry no frontmatter key but `okf_version`. *Why: a typeless file is invisible to
  every tool.*
- **G-W1**: the banner key is not older than the newest `kind: close` entry. *Why: a close that
  did not replace the banner leaves the next session reading stale truth.*
- **G-W2**: at most 2 `kind: pause` entries above the topmost close (G-W2 and G-W6 read the file
  top-down; G-W1 compares keys).
- **G-W3**: no open baton or pause from a session with 2 or more closes/pauses after it. *Why:
  carried work must be done or become a task, not drift.*
- **G-W4**: on every board item, `state: closed` if and only if `status: deprecated`.
- **G-W5**: NOW holds exactly 1 open item (if any are open). NEXT holds at most 5.
- **G-W6**: the newest close has `rows:`, a `guards:` receipt and a `read:` receipt.
- **G-R1**: every `[[routes]]` path in `context.toml` exists, unless the route says
  `optional = true`. *Why: a routing table that points at a moved file sends every reader to
  nothing.*

**Why:** lint is the at-rest check. It catches what a write-time refusal cannot: hand edits, and
records that were valid when written but stale now. A non-empty result is a failure (exit 1).

## The board (tasks and owner questions)

### ce task new

1. Pick the kind: task (`CE-n`) or question (`ASK-n`; prefer `ce ask new`).
2. The brief is at most 120 characters. Every named dep must exist. The tier's cap must have room
   (NOW 1, NEXT 5, counting open items of both kinds). Otherwise, demote something first.
3. Id: the highest number in the series + 1. Count file names *and* `id:` keys, open and closed.
   Never reuse a number.
4. File: `tasks/<id>-<slug>.md`. Slug: lowercase the title; replace each run of characters other
   than ASCII `a-z` and `0-9` (accented letters included) with `-`; strip `-` from both ends. If
   it is over 48 characters, take the first 48 and drop everything from the last `-` on, even a
   whole word. An empty slug gives `tasks/<id>.md`. The slug never changes afterwards.
5. Frontmatter, in order: `type`, `id`, `title`, `brief` (if any), `pri` (default LATER),
   `state: open`, `deps: [...]`, `source: session <key>`, `created: <today>`, `moved: <key>`,
   `updated: <key>`. Body, unless you write your own:

   ```
   <title>.

   ## Traps

   - none yet

   ## Read first

   - none yet

   ## Log
   ```

**Why:** one file per item, with no renames, so every reference keeps working. The caps keep the
board a ranking, not a pile (G-W5). The brief is a constraint, not a summary (FRAMEWORK §5.2).

### ce task set

Change any key except the ones operations own. `state`, `status` and `closed` change by
`close`/`reopen`. `moved` changes by `touch`/`promote`. `pri` by `promote`. `deps` by `dep`.
`last_asked` by `ask raised`/`ask later`. `updated` changes on every write. `type`, `id` and
`body_sha` never change. The brief stays at most 120 characters. Values take the kind's declared
type: an empty value, `null` or `~` means null (so `brief=` clears the brief); a list is
comma-separated, with or without `[...]`; a date is `YYYY-MM-DD`; a key must look like
`2026-10-08e`. A set with no fields still bumps `updated`.

**Why:** the keys with an operation each carry a rule: caps, consistency of `state` and `status`,
`moved` meaning real progress. A raw edit would skip that rule (DEC-14 item 7).

### ce task promote

Item open; `pri` a valid tier; the target tier has room, not counting the item itself. Set `pri`,
`moved: <key>`, `updated: <key>`.

**Why:** re-ranking is progress on the board, so it bumps `moved`, and it is where the caps are
enforced.

### ce task dep

Add (every one must exist and must not be the item itself) or remove ids in `deps`. Keep the
existing order and add new ones at the end.

**Why:** deps decide what an answered question or a closed task unblocks (`ask answer` reports
it), so a dangling or self dep would mislead.

### ce task comment

Append to `## Log` (create the heading at the end if missing) one line
`- <key> (<actor>): <text>`, with further lines indented two spaces (a blank line becomes two
spaces). The section is written as heading, blank line, entries. Never edit an earlier log line.

**Why:** the log is the item's history in place. Appending only keeps it trustworthy.

### ce task touch

Set `moved: <key>` and `updated: <key>`. With `--mechanical`, set only `updated`.

**Why:** `moved` means a person or agent made progress on the item. Housekeeping touches are
mechanical, so they must not look like progress (FRAMEWORK §5.2).

### ce task close

A message is required, and the item must be open. Set `state: closed`, `status: deprecated`,
`closed: <key>`, `moved`, `updated`. Append `- <key> (<actor>): closed: <message>` to `## Log`.
Do not move or rename the file.

**Why:** closed items stay in place as records, so links never break (US-5, AC-12). `status:
deprecated` is the OKF view of the same fact (G-W4). The message says why, e.g. `done in <commit>`.

### ce task reopen

A message is required, and the item must be closed. Set `state: open`, set `closed:` to null,
delete `status`, and set `moved` and `updated`. Append `- <key> (<actor>): reopened: <message>`.

**Why:** the mirror of close, keeping G-W4 true.

### ce task section

Replace the content under `## <name>` up to the next `## ` heading. Add the section at the end if
it is missing. Never `## Log`: use `comment`.

**Why:** Traps and Read first are replaced as they get better. The Log is history, so it is only
ever appended to.

### ce task list

From frontmatter only: open items by default (`--state closed|all`), optionally filtered by
`--pri` or `--label`. Sort by tier (NOW, NEXT, LATER, SOMEDAY), then prefix alphabetically (ASK
before CE), then number. One line each: pri and id each padded to 7 characters, the title, then
`  (closed <key>)` and `  [deps: a, b]` where they apply. No match prints `no matching items`.

**Why:** the board view comes from the records, never the other way round (board size 2). Reading
frontmatter only keeps it cheap (AC-13).

### ce task show

Print `id · pri · state · title`, then the brief and deps, then the body with `## Log` cut to its
5 newest entries, newest first (`--head 0` for all), or just one `--section`.

**Why:** read-only and bounded. The Log grows without limit, and the newest entries are the ones
that matter.

## Owner questions

### ce ask new

As `task new` with kind question, default `pri: NEXT`, plus `last_asked:` (null) and
`blocks: [...]` if it blocks items. Default body:

```
**Question:** <title>

**Why owner-only:**

**Options:**

**Blocks:** <ids or none>

## Log
```

Then raise it in chat this session. Ids in `blocks` are not checked to exist (deps are), so
check them yourself.

**Why:** a question waiting on the owner is a board item, so it is ranked and gets raised, never
buried in prose (FRAMEWORK §5.3). "Why owner-only" makes the asker check that it really is the
owner's call (P8).

### ce ask raised

After raising questions in chat: each must be a question, and your session must have an open
stub. Set `last_asked: <key>` (and `updated`) on each. In your stub, delete any `- **asked:**`
line and add one at the end, with no blank line before it:
`- **asked:** <every id raised so far this session>`. The engine does not check that a question
is still open.

**Why:** the stamp resets the overdue clock. The stub line is the receipt that `session close`
checks (G-W8).

### ce ask later

The owner said "later". Set `last_asked: <key>` and append
`- <key> (<actor>): owner said later; still open`. Do not close it. This writes no `asked:` line
in your stub, so a deferred question at NOW or NEXT must still be named in your close's `asked`,
or demoted to LATER.

**Why:** "later" is not an answer. The question stays open, and the clock restarts (FRAMEWORK
§5.3).

### ce ask answer

1. The question must be open, and you need the owner's words verbatim.
2. New decision `DEC-n`: `title`, `actor: owner`, `decided: <today>`, `session: <key>`,
   `decision_status: PROVISIONAL`, `answers: ASK-n`. Body:
   `Owner, answering ASK-n: *"<words>"*`. Stamp its `body_sha` at once.
3. On the question, set `state: closed`, `status: deprecated`, `closed: <key>`,
   `last_asked: <key>`, `answered: {on: <today>, session: <key>, decision: DEC-n}` and `updated`.
   Append `- <key> (<actor>): answered by the owner: DEC-n`.
4. Report what it unblocks: open items whose deps include it and whose deps are now all closed,
   plus everything in its `blocks`.

**Why:** an answer is a decision in the owner's own words. It is stamped so the words cannot
drift, and closing the question points to the decision rather than burying the answer in a log
line (FRAMEWORK §6.2).

## Batons and pauses

### ce baton add

New `BTN-n` in `docs/working/`: `title` (first line of the step, cut to 100 characters, never
refused), `session: <key>`, `state: open`, `created: <today>`, `why` (`''` if none given). Body:
`<step>` + blank line + `**Why skipped:** <why or "not given">`.

**Why:** a step skipped at close must reach the next session as a record, not as a sentence in a
note that the next banner overwrites (FRAMEWORK §5.4).

### ce baton done

Evidence is required: the commit, file or ledger entry that shows the step done. The baton must be
open. Set `state: done`, `done: <key>`, `evidence: <text>`.

**Why:** without evidence, "done" cannot be checked.

### ce baton expire

Housekeeping: actor `process:housekeep` unless the caller gives one. For every open baton or
pause from a session with 2 or more closes/pauses after it:
1. new task at LATER, titled `Expired <id>: <title>` (cut to 120 characters), `source: <id>`,
   body: the task body template with its first line replaced by
   `Expired <id> from session <s>: <title>. Converted by housekeeping (G-W3); read <path>.`
   No cap check: LATER has none.
2. on the baton or pause, set `state: expired` and `expired_to: <new task id>`.

Both writes are `mechanical: true` in the op log.

**Why:** carried work must not drift for ever, and turning it into a task keeps it without
blocking orientation (G-W3, AC-15).

### ce pause open

1. Read the branch (`git rev-parse --abbrev-ref HEAD`) and every uncommitted path, untracked files
   included (`git status --porcelain=v1 --untracked-files=all`; for a rename take the new path),
   from git itself.
2. New `PAU-n`: `title` (first line of what was in flight, cut to 100 characters), `session`, `state: open`, `created`,
   `branch`, `uncommitted: [...]`, `resume_step`, `evidence` (or `none`), `deferred: [...]`. Body:
   `**In flight:** ...` + blank line + `**Resume step:** ...`.
3. Commit that file alone, at once: `git add -- <path>`, then
   `git commit --only -m "pause PAU-n (<key>): <first 60 characters of the title>" -- <path>`.
   (`--only` on a file git has never seen fails without the `add`.)

**Why:** the next session needs the exact state of the tree, which comes from git, not from
memory. Committing at once keeps another session's close from sweeping it away (FRAMEWORK §5.5
rule 4, AC-14).

### ce pause resume

The pause must be open. Set `state: done`, `resumed: <key>`.

**Why:** closes the loop so `orient` stops listing it, and records who picked it up.

## The banner

### ce banner show

Print the banner's key, its hash (above) and its text. Keep the hash: `banner set` needs it.

**Why:** reading and hashing together is what makes the later write safe.

### ce banner set

1. Re-read `HANDOFF.md` and recompute the banner hash. If it differs from the one you saw, stop.
   Another session wrote it: read theirs, merge, and start again.
2. Replace the heading and text up to the next `## ` heading with `## Banner (<your key>)`, a
   blank line, and your text; add a blank line after it only if something follows. Keep the
   note's line endings.

**Why:** the banner carries exactly one session key, and a later close must not silently erase
another session's truth (FRAMEWORK §5.5 rule 2, AC-16).

## Append-only records (decisions and stories)

### ce record new

1. Take the next free id in the kind's series (as `ce task new`): `DEC-n` in `docs/decisions`,
   `US-n` in `docs/stories`, file `<id>-<slug>.md`.
2. Frontmatter: `type`, `id`, `title`, then the keys you were given. Any **required** key you
   were not given is filled only if it can mean nothing but now: a date-typed key (`decided`,
   `date`) with today, a key-typed one (`session`) with your session key. Everything else
   required, `actor` above all, must be given; if it is missing, stop.
3. Body: the text, verbatim (owner words keep their line breaks), one final newline.
4. Stamp it at once (`ce record stamp`): `body_sha` is the last frontmatter key.

**Why:** owner intent is recorded verbatim, now (§6.2), and a record born stamped can never be
quietly rewritten. Who decided is never guessed: an `actor: owner` on the agent's own call is
the worst error this file can hold.

### ce record stamp

On each named decision or story with no `body_sha`, once its body is final: add
`body_sha: sha256:<hex>` (the body hash above) as the last frontmatter key. Never replace an
existing stamp. Check every named record first; if any is not append-only or is already
stamped, stamp none of them.

**Why:** stamping freezes the owner's words (G-D10). Stamping too early freezes a draft, and
every later fix then has to be an amendment.

### ce record amend

The only body change an append-only record takes. If the record is stamped, its hash must match
first. If there is no `## Amendments` heading, add one at the end. Then append a blank line and
`- **<key> (<actor>):** <first line>`, with further lines indented two spaces (blank lines stay
blank).

**Why:** owner intent changes by addition, so the original words and every change stay readable
in order, and the hash above the heading still holds.
