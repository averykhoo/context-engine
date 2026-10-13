---
type: Runbook
title: "Manual mode: every engine operation done by hand, and why each step exists"
source: FRAMEWORK P16, §7.5
created: 2026-10-08
---

# Manual mode

Every operation the engine (`context-engine`, `python -m context_engine`) performs, written as steps a person
or an agent can follow with a text editor, git and a SHA-256 tool. It exists for two reasons
(FRAMEWORK P16):

1. **Fallback.** A repo with no Python can still run the framework: slowly, by hand, with the
   same files and the same rules.
2. **Reference behaviour.** Each step says **why** it exists. When the engine errors, refuses
   oddly or writes something that looks wrong, this is the statement of what the right result
   was, so the agent can finish the job by hand *and* fix the engine.

In the engine repo, a test fails the gate if any `context-engine` subcommand has no
`### context-engine <group> <op>` section here, or a section has no **Why**. The order in which
a ritual runs these operations is the companion runbook, [rituals.md](rituals.md).

## When the engine and this runbook disagree

- **A refusal is not a bug.** Refusals are the engine doing its job: every one prints a remedy.
  Do what the remedy says. Only treat a refusal as a bug when the Why below says the write should
  have been allowed.
- **The engine is wrong** (it wrote what this runbook says it must not, or refused what it must
  allow): finish the step by hand from this runbook, then fix the engine with a test that fails
  first (break the code, watch the test go red, restore), and name the step here in the commit message.
- **This runbook is wrong** (the engine is right and the text is stale): fix the text in the same
  commit as the code it describes. The Why is the tiebreaker: whichever side serves it wins.
- **Neither is clearly right:** it is a decision. Record it as a decision, or ask the owner if it
  changes what they asked for.

## When the MCP tools are missing

The MCP server is a thin layer over the same functions the CLI calls, so nothing is lost
without it:

1. Run every operation as `<interpreter> -m context_engine ...` for the rest of the session.
2. Register the server once for this machine: `claude mcp add --scope local context-engine --
   <interpreter> -m context_engine.mcp`. Check it with `claude mcp get context-engine`.
3. Tell the owner to restart Claude Code; the tools appear at the next start.

**Why:** Claude Code starts MCP servers only when a session launches, so nothing done mid-session
brings the tools in. The local registration carries the interpreter's absolute path outside the
repo, so the checked-in `.mcp.json` stays machine-neutral. Its `${CE_PYTHON}` works only if the
variable was in Claude Code's starting environment; an `env` block in
`.claude/settings.local.json` reaches the agent's shell but not `.mcp.json`.

## What every write does

These hold for every operation below. The per-operation sections only list what is extra.

| Rule | By hand | Why |
|---|---|---|
| **Take the lock** | No lock exists by hand. Instead: re-read the file immediately before editing it, and run `git status` and `git log -3` before committing. | Several sessions share one checkout. The engine's OS lock stops two writers losing each other's change; by hand, re-reading is the only defence. |
| **Check the caller** | Know your session key (like `2026-10-08e`) and your actor (`human:<id>`, `process:<id>`, or `<producer>/<version>` such as `claude-code/<model-id>`). Every write below records them. | Each write has to say which session made it and who did it. Without that, nobody can find a change or trace it back (OKF §7). |
| **Validate before writing** | Check the result against its kind's schema (table below). If it fails, do not save it. | A bad record that reaches disk breaks every later reader. The engine checks before writing any byte. |
| **Change only your own lines** | Edit only the frontmatter keys the operation names. Keep every other line exactly as it was: order, quoting, comments, unknown keys. Keep the file's line endings. | Byte-stable writes keep diffs reviewable and keep keys that other tools own (OKF §4.1). |
| **YAML shapes** | Lists in flow style: `deps: [T-2, T-3]`. Dates unquoted: `created: 2026-10-08`. Null is the bare key: `closed:`. Quote any value with `: ` in it. | Quoted dates fail the `date` type, and an unquoted colon makes the YAML mean something else or fail to parse. |
| **New keys go last** | A key the record does not have yet (`status`, `closed`, `answered`, `done`, `evidence`, `resumed`, `expired_to`, `body_sha`) is added after the last key. An existing key is replaced where it stands, keeping an end-of-line comment. | Keeps every untouched line in place, so the diff shows only the change. |
| **New records** | Frontmatter, the closing `---`, one blank line, the body, one final newline. `deps: []` is written even when empty. | One shape for every record keeps hand-written and engine-written files identical. |
| **Bump `updated`** | On every write to a board item (task or question), set `updated: <session key>`. | It is how a reader sees a record was touched this session without reading the op log. |
| **Log the operation** | Append one line to `docs/ledger/ops.jsonl` (format below). | The op log is the audit trail: who changed which keys, in which session. G-W7 reads it. |
| **Engine-owned keys** | Never hand-edit `type`, `id` or `body_sha` on an existing record. | Ids are never reused or renumbered (P3). `body_sha` pins an owner's words (G-D10). |

**Op log line**, one JSON object per line, UTF-8, `\n` endings:

```json
{"at": "2026-10-08T18:10:28+08:00", "session": "2026-10-08e", "actor": "claude-code/<model-id>", "op": "close", "id": "T-8", "path": "tasks/T-8-dogfood-adoption.md", "fields": ["state", "status", "closed", "moved", "updated", "body"], "mechanical": false}
```

`at` is local time with its offset. `fields` lists the keys changed, plus `"body"` if the body
changed. `mechanical` is `true` only for housekeeping and the `--mechanical` flag.

| Operation | `op` | `id`, `path` | `fields` |
|---|---|---|---|
| any new record (task, question, decision, baton, pause) | `new` | the record | every frontmatter key, `type`, `id` and `body_sha` included |
| task set, promote, dep, comment, touch, close, reopen, section | `set`, `promote`, `dep`, `comment`, `touch`, `close`, `reopen`, `section` | the item | the changed keys, then `updated`, then `body` if the body changed |
| ask raised | `ask.raised` | one line per question, then one with id = session key, path = the ledger | `["last_asked", "updated"]`; the ledger line `["asked"]` |
| ask later, ask answer | `ask.later`, `ask.answer` (answer also writes a `new` line for its `D-n`) | the question | the changed keys, `updated`, `body` |
| baton done, pause resume | `baton.done`, `pause.resume` | the record | the changed keys |
| baton expire | `new` then `hk.expire_batons`, both mechanical | the task, then the baton or pause | as above |
| session start, close, pause | `session.start`, `session.close`, `session.pause` | id = session key, path = the ledger | `["kind"]` |
| banner set | `banner.set` | id = session key, path = `HANDOFF.md` | `["banner"]` |
| record stamp, record amend | `stamp` (one line per id), `amend` | the record | `["body_sha"]`; `[]` |
| record correct | `correct` | the record | `["body_sha", "body"]` |
| decision supersede, decision link | `supersede`, `link`: one line per record changed | the record | the changed keys |
| decision relink | `relink` | the decision | `["code"]` |
| decision set | `set` | the decision | the changed keys (no `updated`: decisions do not carry it) |
| decision import | `import`, one line per record | the record | every frontmatter key |
| any write to a decision, when `decision_index` is set and the index changed | `index`, mechanical | id `index`, path = the index | `["index"]` |
| task close of an item with residuals | `register.append`, before the `close` line | the task, path = the register | the new INV ids |

### Record kinds (the kit's defaults)

| Kind | Id | Directory | Mode | Required keys | Enums and types |
|---|---|---|---|---|---|
| decision | `D-n` | `docs/decisions` | append-only | title, actor, decided, session, decision_status | decision_status: BUILT, PROVISIONAL, DEFERRED, SUPERSEDED, REJECTED; decided date; session key |
| story | `S-n` | `docs/stories` | append-only | title, actor, date, story_status, goals | story_status: live, unspecified, unconfirmed, retired; date date; goals list |
| task | `T-n` | `tasks` | replaced | title, pri, state, created | pri: NOW, NEXT, LATER, SOMEDAY; state: open, closed; created date; moved, updated, closed keys; deps, labels lists |
| question | `ASK-n` | `tasks` | replaced | title, pri, state, created | as task, plus blocks list, last_asked key |
| baton | `BTN-n` | `docs/working` | stamped | title, session, state, created | state: open, done, expired; session, done keys; created date |
| pause | `PAU-n` | `docs/working` | stamped | title, session, state, created, branch, resume_step | state: open, done, expired; session, resumed keys; created date; uncommitted, deferred lists |

The repo's own `context.toml` is the authority: its `[kinds.<name>]` tables set each kind's
prefix, directory, required keys and types, and a repo may have changed any of them. Read it
before writing a record by hand.

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
  `sha256:` + the full hex SHA-256 of those UTF-8 bytes. A record with `corrected:` lines is
  hashed with its corrections undone first (§ context-engine record correct), so the hash always
  pins the words as typed. *Why: it makes "verbatim" checkable. Rewriting an owner's words
  changes the hash (G-D10), and amendments sit below the cut so they never break it.*
- **Banner hash**: take the `## Banner (<key>)` heading line through to the next `## ` heading,
  or to the end of the file if there is none. Convert to LF and strip leading and trailing `\n` characters. Then `sha256:` + the **first 16** hex
  characters. *Why: `banner set` must refuse when another session rewrote the banner since you
  read it (FRAMEWORK §5.5 rule 2).*

By hand: `printf '%s\n' "$text" | sha256sum` (Git Bash), or
`Get-FileHash -Algorithm SHA256` on a file holding exactly the canonical bytes (PowerShell).
The hex is **lowercase**: `Get-FileHash` and `certutil -hashfile` print uppercase, so lower it.
The bytes are UTF-8 **without a BOM**: PowerShell 5.1's `-Encoding utf8` writes one, so write
the file another way (the Write tool, or `[IO.File]::WriteAllText(path, text)`). *Why: a
different case or one extra BOM gives a hash that never matches the engine's.*

---

## Sessions

### context-engine session start

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
leaves evidence if the session dies (G-W11) (FRAMEWORK §5.5 rule 1). The banner key
counts too, because a session may have written the banner before its ledger entry.

### context-engine session close

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

   - **rows:** T-8 (runbook written); S-11 (amended)
   - **receipts:**
     - guards: gate pytest -q green, N passed; context-engine lint: ...
     - read: ...
     - asked: none open
   - **summary** (the owner digest):
     - one line per point, 1 to 7 of them
   - **Still owed:**
     - nothing
   ```
   Leave out the `asked:` line if it is empty. Op log: `session.close`, fields `["kind"]`.

**Why:** the close is what the next session trusts. The receipts prove the gate ran and say
what was read. The asked check stops owner questions going unraised for days (G-W6, G-W8). The 7-line cap keeps the digest something the owner will actually read (FRAMEWORK §5.6).

### context-engine session pause

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

### context-engine orient

Read and report, in this order, in under 6000 bytes in total (`orient_max_bytes`). If a part does
not fit, cut it at a line and say where the rest is:

0. only when G-D0 fails (§ lint), and `[guards] off` does not name it: a `Contract: fix this
   first` section, one line per failure with its remedy;
1. the banner (`HANDOFF.md` § Banner);
2. open batons and pauses (`docs/working/`, `state: open`), your own session's first, each pause
   with its resume step and branch;
3. other sessions with an open stub in the ledger, which the session then shows the owner, one
   line each (`rituals.md` § Session start); say `none` when there are none;
4. board items at NOW and NEXT (as `context-engine task list`);
5. owner questions to raise now: open at NOW or NEXT, or overdue (see session close step 3);
6. the NOW item's brief, `## Traps` and `## Read first`;
7. in a repo whose `[working] register` is not the engine's own `REGISTER.md`: one line,
   `Engine register (<version>): <N> residual risks, context-engine register show --engine`.

**Why:** one bounded read at session start replaces opening a dozen files. The
order is the order of urgency: a contract that did not load, then carried work and live sessions,
then new work. A `SessionStart` hook runs it in an adopted repo (kit README § Hook), with no
session key; a failing hook is silent, so a session that finds no orient output in its context
does this by hand.

### context-engine routes

Read the `[[routes]]` entries in `context.toml`, in order. Each names a component, its path
(plus `pattern`, how files under it are named), its change `mode`, and an optional `note`.

**Why:** before writing anything, know where it belongs and whether it may be edited, replaced,
or only appended to. The table used to sit in `CLAUDE.md`; it lives in config now so the engine
can check it (G-R1) and every repo can carry its own (FRAMEWORK §2).

### context-engine lint

Check every record, then the working state. `--working` does only the second half.

- **schema**: every record in a kind's directory whose name starts with its id parses (valid
  YAML, a closing `---`), has the right `type` and `id`, every required key, enum values in
  range, values of the declared type, and an OKF `status` from draft/stable/deprecated.
- **G-D10**: every append-only record (decision, story) has `body_sha`; its `corrected:` lines
  each match the body; and with them undone, the body hash above matches `body_sha`. *Why:
  owner words are verbatim, so a rewrite must show up, and so must a bracket whose `corrected:`
  line was dropped.*
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
- **G-W4**: on every board item, `state: closed` if and only if `status: deprecated`; and no
  open question carries `answered:` (an answered question never reopens, § task reopen).
- **G-W5**: NOW holds exactly 1 open item (if any are open). NEXT holds at most 5.
- **G-W6**: the newest close has `rows:`, a `guards:` receipt and a `read:` receipt.
- **G-W12**: an open item at NOW that carries `review:` passes the design-review checks of
  `task promote`. *Why: the promotion refused it, so a failing review there was edited by hand.*
- **G-W13**: every `- residual:` line of a closed item carrying `review:` has a register entry
  with the same risk text and that task in `from:`; every register entry has `affects`, `why not
  eliminated`, `control` and `from` lines; no two entries share an INV id. *Why: the register is
  what is handed over, so a residual missing from it is a risk nobody downstream is told about.*
- **G-R1**: every `[[routes]]` path in `context.toml` exists, unless the route says
  `optional = true`. *Why: a routing table that points at a moved file sends every reader to
  nothing.*
- **G-D0**: the contract (`contract` in `[engine]` of `context.toml`, `CLAUDE.md` by default)
  exists; it has at least one line starting `framework:`; every such line's value is
  `major.minor` or `major.minor.*` (no patch, no `-draft`; words after the value are a comment);
  and that major.minor, and the version in any `<!-- context-engine kit X.Y begin -->` marker,
  equal the first two numbers of the installed engine's version (`<engine-python> -m pip show
  context-engine`, or `context_engine.__version__`). *Why: the pin says which engine the repo's
  rules were written for; a stale one means the rules and the tool disagree.* When the contract
  holds a kit block of that version: the text between its markers is exactly the engine's
  `kit/bootloader.md` block (not the inline block of a kit from before the bootloader, not a hand
  edit, and with its end marker), and every `@<path>` line in it names a file, resolved against
  the contract's own directory, that exists and equals the engine's `kit/contract.md` once line
  endings are ignored (`git diff --no-index --ignore-cr-at-eol`). *Why: Claude Code loads the
  framework's rules through that import, and the framework owns the file; a missing or edited
  copy means a session runs on rules nobody shipped.*
- **G-D1**: for each `[[routes]]` entry with `max_lines`, `max_bytes` or `max_width`, the routed
  file (or each `.md` under a routed directory) has at most that many lines and bytes, and no
  line wider than that many characters except table rows (lines starting `|`). *Why: a place
  with no cap bloats (FRAMEWORK P6); the cap makes the way out (archive, ledger, a decision) due.*
- **G-D2**: in each kind's directories no two files carry the same id, by file name or by `id:`;
  and no id appears in two `new` or `import` lines of the op log. *Why: an id is never reused (P3).*
- **G-D3**: in each file `[guards] links` lists (each `.md` under a listed directory; skip a
  record with `status: deprecated`), outside fenced code: every relative link `[x](path#anchor)`
  and `[x]: path` names a file that exists with exactly that case, relative to the doc, and its
  anchor is a heading there (GitHub's slug: lower case, punctuation dropped, spaces to hyphens);
  every backticked `path::Name.attr` names a file that exists case-exact (a bare file name may be
  anywhere in the repo) whose text has each dotted part as a word. *Why: a dead reference sends
  the reader to nothing, and on Windows a wrong case still opens.*
- **G-T3**: in each file `[guards] existence` lists, skipping fenced code, blockquotes and lines
  with `*HISTORY —*`: every backticked name of a file (a path with a `/`, or a name ending in a
  text extension such as `.py` or `.md`) exists case-exact, and every `file::symbol` resolves as
  for G-D3. Spans with spaces, `*`, `<`, or a leading `.` or `/` are not names. Also, every
  `code:` link of a decision that is not `status: deprecated` names a file that exists
  case-exact from the repo root and has each dotted part of its symbol as a word, by the rule
  of § context-engine decision link. *Why:
  normative text that names a file which is gone states a rule nobody can follow, and `why()`
  answers from decision links.*
- **The intent chain** (G-I1, G-I2, G-T1, G-T2, G-T6). Each is off while a source it needs is
  unset: `[guards] charter` (G-I1), `[guards] stories`, the kind holding the stories (G-I1, G-I2,
  G-T1, G-T6), `[working] criteria` (G-T1, G-T2, G-T6) and `[guards] tests` (G-T2). A set path
  that does not exist is red. List three things: the charter's goals (each table row whose first
  cell is a goal id, `G-n`; a legacy `G3` is red there, but reads as `G-3` in a story's `goals`),
  the criteria (each table row whose first cell is an id, with its `from` and `status` cells by the
  table's header; a source column may be headed `from`, `story` or `source`), and the claims (each
  match of the `[guards] claim` pattern, by default `criterion("AC-n")` or `criterion: AC-n`, in
  every file under `[guards] tests`). No goal row, no criterion row, a table of criteria missing
  its `status` or source column, or no claim at all is red: the format changed under the pattern.
  Then: **G-I1**, every story that is not `retired` names at least one goal and only goals of the
  charter, and every goal is named by one such story; no goal id leads two rows. **G-I2**, every
  story's `actor` is `owner`, `human:<id>` or `agent (reconstructed from ...)`, its `date` is
  YYYY-MM-DD, its `story_status` is live, unspecified, unconfirmed or retired, and `unconfirmed`
  goes with an agent's actor only. **G-T1**, every `live` story's id is in the `from` cell of a
  criterion that is not `retired`, and every `unspecified` story's id is a whole word in an open
  board item. **G-T2**, every `tested` or `manual` criterion is claimed, every claimed id is a
  criterion, and every status is planned, tested, manual, deviates or retired. **G-T6**, every
  `from` cell names at least one id, each a story or decision that exists (a criterion's actor is
  its source's). *Why: the chain from goal to test is what makes correct checkable; a link that
  points at nothing looks traced and is not, and a criterion marked tested whose test was deleted
  keeps reading as tested.*
- **G-D12** (only when `[guards]` sets `coverage_spec` or `coverage_maps`; red if only one is
  set, if the spec is missing, or if the `coverage_maps` glob is absolute or has a `..`, matches
  no file, or matches a file with no `YYYY-MM-DD` in its name): outside fenced code in the spec,
  list (1) the bold component name in each numbered row of §2's table, (2) each `### 5.6` and
  `### 6.n` heading as `§6.n`, and (3) every `G-` id (`G-D3`, not `XG-D3` or `G-D3x`); fewer
  than 20, 10 or 30 of a class is red (the engine's floors; a repo whose spec they do not fit
  sets `[guards] off = ["G-D12"]`). Take the newest map by the date and session letters in its
  file name, ordered as session keys (`z` before `aa`). Each listed thing must be a whole cell
  in its class's column of a table in that map: under `Component` for a component (the cell
  may add ` (...)`), under `§` in a table with a `Ritual` column for a ritual, under `Guard`
  for a G-id. Or it appears as a whole word in some board file, open or closed (`§6.1` is not
  `§6.13`, `G-D1` is not `XG-D1`). *Why: a spec that gains a ritual or guard nothing owns
  drifts unseen; the map is frozen, so the fix is a new dated map or a `task new` naming it,
  never an edit.*
- **G-D7**: in each file `[guards] signals` lists, outside fenced code: at most `warn_max` ⚠, at
  most `bold_caps_max` bold spans with a run of four capitals and no lower case (`**NEVER**`),
  and none of `retired_glyphs`. *Why: a signal ranks only while it is rare.*
- **G-D8**: the note (`handoff` in `[working]`) has at most one `## Banner (<key>)` heading, no
  other heading containing a session key, and no banner line that starts with a session key as
  a bullet or in bold. *Why: a note under a replace rule regrows by layering; this is the layer
  detector.*
- **G-D9**: every line of `context.toml` that assigns a number (inline tables too) has a comment
  with `provenance: MEASURED` or `provenance: JUDGEMENT` and `wrong if` (or `wrong as above`),
  and the comment does not cite an example. *Why: a tuned value with no provenance cannot be
  re-judged, and a spec example is neither a measurement nor a judgement.*
- **G-W7**: for each board item and each of `moved`, `updated`, `closed`, `last_asked`: the value
  equals the `session` of the newest op log line for that id whose `fields` lists the key; with
  no such line, the value is older than the log's first session. Every op log line parses as
  JSON. *Why: those keys are written only by operations, so a mismatch is a hand edit.*

A guard id listed in `[guards] off` is not reported (only ids lint reports may be listed). A path
listed in `[guards]` that does not exist is itself a red.

**Why:** lint is the at-rest check. It catches what a write-time refusal cannot: hand edits, and
records that were valid when written but stale now. A non-empty result is a failure (exit 1).

## The board (tasks and owner questions)

### context-engine task new

1. Pick the kind: task (`T-n`) or question (`ASK-n`; prefer `context-engine ask new`).
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

### context-engine task set

Change any key except the ones operations own. `state`, `status` and `closed` change by
`close`/`reopen`. `moved` changes by `touch`/`promote`. `pri` by `promote`. `deps` by `dep`.
`last_asked` by `ask raised`/`ask later`. `answered` by `ask answer` only. `updated` changes on
every write. `type`, `id` and `body_sha` never change. The brief stays at most 120 characters. Values take the kind's declared
type: an empty value, `null` or `~` means null (so `brief=` clears the brief); a list is
comma-separated, with or without `[...]`; a date is `YYYY-MM-DD`; a key must look like
`2026-10-08e`. A set with no fields still bumps `updated`. `review` takes only values from
`[working] review_triggers` (`record-kind`, `guard`, `write-op`, `git-loss`, `long-lived`,
`shipped`): set it on an item above the design-review threshold (FRAMEWORK §5.2). Setting it on
an item already at NOW first checks its `## Design review` as in `task promote`. Do not remove it
from an item whose design review lists a `- residual:` line: close the item to file them, or take
the residual lines out first.

**Why:** the keys with an operation each carry a rule: caps, consistency of `state` and `status`,
`moved` meaning real progress. A raw edit would skip that rule.

### context-engine task promote

Item open; `pri` a valid tier; the target tier has room, not counting the item itself. Set `pri`,
`moved: <key>`, `updated: <key>`. **Moving the NOW item down** can leave NOW short: check NOW as
in § task close and tell the owner.

**Promoting to NOW an item that carries `review:`** (it is above the threshold, FRAMEWORK §5.2):
first check its `## Design review` section by hand, and do not promote while any check fails.
Start a review from this template (the engine knows it verbatim, so a copy left unchanged is
refused):

```
affects: <who can be hurt: the building session, the next session, the owner, a plain-git human, every deployed repo>
- eliminated: <a risk the design cannot produce>
- reduced: <risk> | rung: <reduce|collective> | control: <the refusal, guard or rule, by name>
- residual: <risk> | rung: <reduce|collective|individual> | why: <why it was not eliminated> | control: <the guard or rule, by name>
F: <what will need doing to it later, by whom, how often, and what makes it stale>
A: <how it is read and fixed without the engine>
M: <which forms keep it from drifting>
E: <what it reuses: one name, one format, one runbook section>
```

The checks: no template line left verbatim; an `affects:` line with text; at least one risk
line; every line starting `- ` is `- <class>: <risk>` with class `eliminated`, `reduced` or
`residual`, then ` | key: value` fields from `rung`, `why`, `control`, `affects`; a `reduced`
or `residual` line has a `rung` from `eliminate`, `reduce`, `collective`, `individual` (a
residual is never at `eliminate`; a risk held only at `individual` is a `residual`, P17); a `residual` line has `why` and `control`; and `F:`, `A:`,
`M:` and `E:` lines, each with text. Any other unindented line is an error.

**Why:** re-ranking is progress on the board, so it bumps `moved`, and it is where the caps are
enforced. Promotion to NOW is the last point before building starts, so it is where a design
above the threshold must show whom it can hurt and how each risk is held (P17, P18).

### context-engine task dep

Add (every one must exist and must not be the item itself) or remove ids in `deps`. Keep the
existing order and add new ones at the end.

**Why:** deps decide what an answered question or a closed task unblocks (`ask answer` reports
it), so a dangling or self dep would mislead.

### context-engine task comment

Append to `## Log` (create the heading at the end if missing) one line
`- <key> (<actor>): <text>`, with further lines indented two spaces (a blank line becomes two
spaces). The section is written as heading, blank line, entries. Never edit an earlier log line.

**Why:** the log is the item's history in place. Appending only keeps it trustworthy.

### context-engine task touch

Set `moved: <key>` and `updated: <key>`. With `--mechanical`, set only `updated`.

**Why:** `moved` means a person or agent made progress on the item. Housekeeping touches are
mechanical, so they must not look like progress (FRAMEWORK §5.2).

### context-engine task close

A message is required, and the item must be open. **Never close an owner question (`ASK-n`)
this way:** it closes only on the owner's answer, through `ask answer` (FRAMEWORK §5.3); if the
owner said later, use `ask later`. Set `state: closed`, `status: deprecated`,
`closed: <key>`, `moved`, `updated`. Append `- <key> (<actor>): closed: <message>` to `## Log`.
Do not move or rename the file.

**If the item carries `review:`**, first check its `## Design review` as in `task promote`; if a
check fails, fix the review, do not close. Then copy each `- residual:` line into the register
(`[working] register`; the kit's default is `docs/invariants.md`). Skip a residual already there
with the same risk text and the same task id in its `from:` line. Create the file with the
heading `# Residual-risk register` if it is missing. Each entry takes the next `INV-n` (one above the
highest in the file and in any `register.append` line of the op log, so an id is never reused),
after one blank line:

```
## INV-<n>: <the risk text>

- **affects:** <the line's `affects` field, else the review's `affects:` line>
- **why not eliminated:** <its `why`>
- **control:** <its `rung`>: <its `control`>
- **from:** <task id>, session <key>
```

Log one op line per close that added entries: `op: register.append`, `id` the task, `path` the
register, `fields` the new INV ids. With residuals and no register configured, stop: configure
one first.

**If the item was at NOW**, count the open items at NOW once it is closed. If NOW holds fewer
than its cap (`[working.caps]`, 1 by default) while any item stays open, G-W5 is red from now
on: tell the owner, naming the NEXT items (or saying NEXT is empty), and ask which one to
promote (§ task promote) before you run the gate. Do not pick it yourself. The engine closes
anyway and says the same at the end of its close line. It says nothing when NOW is still at or
over its cap (G-W5's own remedy applies then) or when `[guards] off` names G-W5.

**Why:** closed items stay in place as records, so links never break. `status:
deprecated` is the OKF view of the same fact (G-W4). The message says why, e.g. `done in <commit>`.
A question closed by `task close` would carry no decision in the owner's words, and the agent
would in effect have answered its own question (FRAMEWORK §5.3).
The residuals move to the register at close because that is when the design is final, and the
register is what the next owner of the work reads (P17, FRAMEWORK §7.4; G-W13 checks it).
An empty NOW is said at close, not refused: refusing would block a close the owner wants, and
the next NOW item is the owner's call; said only at the next gate, it turns the gate red before
anything can be committed.

### context-engine task reopen

A message is required, and the item must be closed. **Never reopen an owner question that
carries `answered:`**, and never delete its `answered:`: its answer is a decision (the one
`answered: {decision: D-n}` names). To change the answer, `record amend D-n` or
`decision supersede D-n <new>`, where D-n is the decision that stands now (follow its
`superseded_by`); for a follow-up, `ask new` citing ASK-n and D-n. A question
closed without `answered:` (by a `task close` from before close refused questions) may be
reopened: that is its repair. Set `state: open`, set `closed:` to null, delete `status`, and set `moved` and `updated`.
Append `- <key> (<actor>): reopened: <message>`.

**Why:** the mirror of close, keeping G-W4 true. Reopening an answered question would leave it
open while claiming an answer; clearing `answered:` instead would orphan the decision whose
`answers:` names it, and a second `ask answer` would make two decisions answer one question
(FRAMEWORK §5.3).

### context-engine task section

Replace the content under `## <name>` up to the next `## ` heading. Add the section at the end if
it is missing. Never `## Log`: use `comment`. On an open NOW item carrying `review:`, check the
result's `## Design review` as in `task promote`, and do not write it while a check fails.

**Why:** Traps and Read first are replaced as they get better. The Log is history, so it is only
ever appended to.

### context-engine task list

From frontmatter only: open items by default (`--state closed|all`), optionally filtered by
`--pri` or `--label`. Sort by tier (NOW, NEXT, LATER, SOMEDAY), then prefix alphabetically (ASK
before T), then number. One line each: pri and id each padded to 7 characters, the title, then
`  (closed <key>)` and `  [deps: a, b]` where they apply. No match prints `no matching items`.

**Why:** the board view comes from the records, never the other way round (board size 2). Reading
frontmatter only keeps it cheap.

### context-engine task show

Print `id · pri · state · title`, then the brief and deps, then the body with `## Log` cut to its
5 newest entries, newest first (`--head 0` for all), or just one `--section`.

**Why:** read-only and bounded. The Log grows without limit, and the newest entries are the ones
that matter.

## Owner questions

### context-engine ask new

As `task new` with kind question, default `pri: NEXT`, plus `last_asked:` (null) and
`blocks: [...]` if it blocks items. Default body:

```
**Question:** <title>

**Why owner-only:**

**Options:**

**Recommendation:** <the option, and why in a line; or "none cheap: <why>" (FRAMEWORK §5.3)>

**Blocks:** <ids or none>

## Log
```

Then raise it in chat this session. Ids in `blocks` are not checked to exist (deps are), so
check them yourself.

**Why:** a question waiting on the owner is a board item, so it is ranked and gets raised, never
buried in prose (FRAMEWORK §5.3). "Why owner-only" makes the asker check that it really is the
owner's call (P8).

### context-engine ask raised

After raising questions in chat: each must be a question, and your session must have an open
stub. Set `last_asked: <key>` (and `updated`) on each. In your stub, delete any `- **asked:**`
line and add one at the end, with no blank line before it:
`- **asked:** <every id raised so far this session>`. The engine does not check that a question
is still open.

**Why:** the stamp resets the overdue clock. The stub line is the receipt that `session close`
checks (G-W8).

### context-engine ask later

The owner said "later". Set `last_asked: <key>` and append
`- <key> (<actor>): owner said later; still open`. Do not close it. This writes no `asked:` line
in your stub, so a deferred question at NOW or NEXT must still be named in your close's `asked`,
or demoted to LATER.

**Why:** "later" is not an answer. The question stays open, and the clock restarts (FRAMEWORK
§5.3).

### context-engine ask answer

1. The question must be open and carry no `answered:`, and you need the owner's words verbatim.
   Open with `answered:` means someone reopened it by hand (G-W4): restore `state: closed` and
   `status: deprecated` from git and change the answer through its decision, as in `task reopen`.
2. New decision `D-n`: `title`, `actor: owner`, `decided: <today>`, `session: <key>`,
   `decision_status: PROVISIONAL`, `answers: ASK-n`. Body:
   `Owner, answering ASK-n: *"<words>"*`. Stamp its `body_sha` at once.
3. On the question, set `state: closed`, `status: deprecated`, `closed: <key>`,
   `last_asked: <key>`, `answered: {on: <today>, session: <key>, decision: D-n}` and `updated`.
   Append `- <key> (<actor>): answered by the owner: D-n`.
4. Report what it unblocks: open items whose deps include it and whose deps are now all closed,
   plus everything in its `blocks`.
5. If the question was at NOW, check NOW as in § task close and tell the owner.

**Why:** an answer is a decision in the owner's own words. It is stamped so the words cannot
drift, and closing the question points to the decision rather than burying the answer in a log
line (FRAMEWORK §6.2).

## Batons and pauses

### context-engine baton add

New `BTN-n` in `docs/working/`: `title` (first line of the step, cut to 100 characters, never
refused), `session: <key>`, `state: open`, `created: <today>`, `why` (`''` if none given). Body:
`<step>` + blank line + `**Why skipped:** <why or "not given">`.

**Why:** a step skipped at close must reach the next session as a record, not as a sentence in a
note that the next banner overwrites (FRAMEWORK §5.4).

### context-engine baton done

Evidence is required: the commit, file or ledger entry that shows the step done. The baton must be
open. Set `state: done`, `done: <key>`, `evidence: <text>`.

**Why:** without evidence, "done" cannot be checked.

### context-engine baton expire

Over MCP this is the tool `mcp__context-engine__hk_expire_batons`, not `baton_expire`.

Housekeeping: actor `process:housekeep` unless the caller gives one. For every open baton or
pause from a session with 2 or more closes/pauses after it:
1. new task at LATER, titled `Expired <id>: <title>` (cut to 120 characters), `source: <id>`,
   body: the task body template with its first line replaced by
   `Expired <id> from session <s>: <title>. Converted by housekeeping (G-W3); read <path>.`
   No cap check: LATER has none.
2. on the baton or pause, set `state: expired` and `expired_to: <new task id>`.

Both writes are `mechanical: true` in the op log.

**Why:** carried work must not drift for ever, and turning it into a task keeps it without
blocking orientation (G-W3).

### context-engine pause open

1. Read the branch (`git rev-parse --abbrev-ref HEAD`) and every uncommitted path, untracked files
   included (`git status --porcelain=v1 --untracked-files=all`; for a rename take the new path),
   from git itself.
2. New `PAU-n`: `title` (first line of what was in flight, cut to 100 characters), `session`, `state: open`, `created`,
   `branch`, `uncommitted: [...]`, `resume_step`, `evidence` (or `none`), `deferred: [...]`. Body:
   `**In flight:** ...` + blank line + `**Resume step:** ...`.
3. Commit that file alone, at once: `git add -- <path>`, then
   `git commit --only -m "pause PAU-n (<key>): <first 60 characters of the title>" -m "Session: <key>" -- <path>`.
   (`--only` on a file git has never seen fails without the `add`. The second `-m` is the
   `Session:` trailer every agent commit ends with, FRAMEWORK §6.10.)

**Why:** the next session needs the exact state of the tree, which comes from git, not from
memory. Committing at once keeps another session's close from sweeping it away (FRAMEWORK §5.5
rule 4).

### context-engine pause resume

The pause must be open. Set `state: done`, `resumed: <key>`.

**Why:** closes the loop so `orient` stops listing it, and records who picked it up.

## The residual-risk register

### context-engine register show

Read the register file named by `[working] register` (the kit's default is `docs/invariants.md`).
Print `register <path>: <N> residual risks`, then for each `## INV-n: <risk>` entry, a blank
line, `INV-n: <risk>` and its `affects`, `why not eliminated`, `control` and `from` lines, each
indented two spaces. With `--engine`, read instead the `REGISTER.md` inside the installed
`context_engine` package (`<interpreter> -c "import context_engine, os;
print(os.path.dirname(context_engine.__file__))"` prints the directory) and say `engine
<version>` for the path.

**Why:** the register is handed over with the work (P17, regs. 7 and 11). The engine's own
register ships inside the package, so a repo the engine is pointed at can read what the engine
cannot protect it from, without a checkout of the engine (FRAMEWORK §7.4).

## The banner

### context-engine banner show

Print the banner's key, its hash (above) and its text. Keep the hash: `banner set` needs it.
If the note has no `## Banner (<key>)` heading yet (or there is no note), the hash is `none`.

**Why:** reading and hashing together is what makes the later write safe.

### context-engine banner set

1. Re-read `HANDOFF.md` and recompute the banner hash. If it differs from the one you saw, stop.
   Another session wrote it: read theirs, merge, and start again.
2. Replace the heading and text up to the next `## ` heading with `## Banner (<your key>)`, a
   blank line, and your text; add a blank line after it only if something follows. Keep the
   note's line endings.
3. **The first banner** (the hash you saw was `none`): insert the same block just before the
   note's first `## ` heading, so that heading still ends the banner; with no `## ` heading,
   append it after a blank line. Create the note if it does not exist.

**Why:** the banner carries exactly one session key, and a later close must not silently erase
another session's truth (FRAMEWORK §5.5 rule 2).

## Append-only records (decisions and stories)

### context-engine record new

1. Take the next free id in the kind's series (as `context-engine task new`): `D-n` in `docs/decisions`,
   `S-n` in `docs/stories`, file `<id>-<slug>.md`.
2. Frontmatter: `type`, `id`, `title`, then the keys you were given. Any **required** key you
   were not given is filled only if it can mean nothing but now: a date-typed key (`decided`,
   `date`) with today, a key-typed one (`session`) with your session key. Everything else
   required, `actor` above all, must be given; if it is missing, stop. For a story (the kind
   `[guards] stories` names), stop too unless it passes G-I2 and G-I1 of § context-engine lint:
   `actor` is `owner`, `human:<id>` or `agent (reconstructed from ...)`, `story_status` is from the
   vocabulary, and `goals` names at least one goal of the charter, each written `G-n`.
3. Body: the text, verbatim (owner words keep their line breaks), one final newline.
4. Stamp it at once (`context-engine record stamp`): `body_sha` is the last frontmatter key.

**Why:** owner intent is recorded verbatim, now (§6.2), and a record born stamped can never be
quietly rewritten. Who decided is never guessed: an `actor: owner` on the agent's own call is
the worst error this file can hold.

### context-engine record stamp

On each named decision or story with no `body_sha`, once its body is final: add
`body_sha: sha256:<hex>` (the body hash above) as the last frontmatter key. Never replace an
existing stamp. Check every named record first; if any is not append-only or is already
stamped, stamp none of them.

**Why:** stamping freezes the owner's words (G-D10). Stamping too early freezes a draft, and
every later fix then has to be an amendment.

### context-engine record amend

The only body change an append-only record takes. If the record is stamped, its hash must match
first. If there is no `## Amendments` heading, add one at the end. Then append a blank line and
`- **<key> (<actor>):** <first line>`, with further lines indented two spaces (blank lines stay
blank).

**Why:** owner intent changes by addition, so the original words and every change stay readable
in order, and the hash above the heading still holds.

### context-engine record correct

A bracketed insertion into a stamped decision or story (any append-only record): a typo, a
missing word, a `[sic]`. It only inserts.
1. The record must be stamped and its hash must match (as `context-engine record amend`).
2. Take the original text: the body above `## Amendments`, in the body hash's canonical form
   (LF, outer newlines stripped, one final `\n`; § The two hashes). Find `after` in it: it must
   occur exactly once (count overlapping matches); if it is missing or occurs twice, stop and
   pick a longer anchor. The anchor and the text are each one line.
3. Insert `[text]` right after it. Note the offset: the number of characters (not bytes) of the
   canonical text before the `[`.
4. Append an amendment as in § context-engine record amend, with the text
   `corrected: at <offset> (+<length of [text]>) inserted "[text]" after "<after>"`.
5. Leave `body_sha` alone: it pins the words as typed, and a stamp is never replaced.

Undoing the corrections newest first (remove `<length>` characters at `<offset>`) gives back
the original text exactly; lint G-D10 does that, fails a record whose `corrected:` lines do not
match, and hashes the result against `body_sha`, so a bracket whose `corrected:` line was
deleted fails too.

**Why:** a strict body hash would forbid fixing a typo, and a free edit would let anything
change. An insertion that can always be undone keeps the words as typed readable under the fix
(FRAMEWORK §6.5); a change of meaning is an amendment, never a correction.

## Decisions

The decision kind is the one `[working] decision` names. Its link fields are lists:
`supersedes` / `superseded_by`, `relaxes` / `narrowed_by` (each pair written together),
`creates`, `amends`, `retires`, `tasks`, `code` (`file` or `file::symbol`) and `refs`.
**Every write to a decision also regenerates the index** (§ context-engine decision index) when
`[working] decision_index` is set; by hand, do that step after each one.

### context-engine decision supersede

`<new>` replaces `<old>`. Both must be decisions; `<new>` must not be SUPERSEDED or REJECTED
itself, and must not already supersede `<old>`. Re-read both files, then in one change:
on `<old>` set `decision_status: SUPERSEDED`, `status: deprecated` and add `<new>` to
`superseded_by`; on `<new>` add `<old>` to `supersedes`. Log one `supersede` line per file.

**Why:** a link written in one direction only is a half-truth, and the engine writes both under
one lock. `status: deprecated` is OKF's word for "kept for history, no longer current" (§9.3).

### context-engine decision set

Set or unset a decision's own frontmatter keys: `decision_status`, `reopen_if` (a REJECTED
decision only: what would justify reopening it), `tags`, `title`, `description`, and any key no
operation owns. Values take the kind's declared types, as in § context-engine task set
(`tags=a, b` is a list; an empty value means null). Refuse, and write nothing, when:
- the key is `type`, `id` or `body_sha` (engine-owned, never changed);
- the key is `status`, `supersedes` or `superseded_by`: use `decision supersede`, which writes
  both directions and the derived OKF status;
- the key is a link field (`relaxes`, `creates`, `amends`, `retires`, `tasks`, `code`, `refs`):
  use `decision link`, or `decision relink` to move a `code` link; no operation removes an id
  link (ids are never reused, so one never goes stale);
- the key is `narrowed_by`: it is the backlink `relaxes` writes, so run `decision link <other>
  <id> --rel relaxes` on the decision that narrows this one;
- the key is `answers` (written once by `ask answer`), or provenance: `actor`, `decided`,
  `session`, `attribution`, `imported_from` or `generated` (who decided, when, in which session
  and from what source are fixed at birth; note a correction with `record amend`);
- the key is `verified` (the owner endorsed it): an endorsement is the owner's words, so record
  them with `record amend <id> "<the owner's words>"`;
- the key is `reopen_if` and the decision would not be REJECTED after the change, or the change
  moves a decision off REJECTED and keeps its `reopen_if` (unset it in the same call);
- the new `decision_status` is `SUPERSEDED`: use `decision supersede <id> <new>`;
- the decision is already SUPERSEDED and the change touches `decision_status`: a superseded
  decision stays superseded; to bring it back, record a new decision and supersede the one that
  replaced it.

Re-read the file, then change only the named keys in place (a new key goes last). The body and
`body_sha` do not change. Log one `set` line with the changed keys, then regenerate the index
(§ context-engine decision index). **Move an owner's decision's status (PROVISIONAL to BUILT, or
to REJECTED or DEFERRED) only on the owner's words, recorded first** (`record amend <id>
"<words>"`): the engine cannot tell whether the owner said so, so this rule is the only control.

**Why:** a decision's status, tags and `reopen_if` are not covered by `body_sha`, so they can be
kept current without touching the words; but the keys other operations own carry a rule
(both directions of a link, the derived OKF status, who decided), and a raw edit would skip it.

### context-engine decision link

Add `<target>` to one link field of a decision. `--rel` names the field; without it, a board
item's id goes to `tasks` and anything with `::` or `/` to `code`; a decision needs
`--rel relaxes` (which also adds this decision to the other's `narrowed_by`). Check the target
first: a record id must exist; a criterion id must be a row (`| AC-n |`) of the criteria file
`[working] criteria` names; any other id is refused; a `code` path must be written from the
repo root with `/` (no `\`, no `..`, no leading `/` or drive), name a file (not a directory or
the root) that exists with its exact case, and every dotted part of its symbol must be
non-empty and appear in the file. A target already in the
field is a no-op: stop.

**Why:** `why()` answers from these links, so a link to something that does not exist answers
wrongly. Existence is checked when the link is written; G-T3 fails a current decision's link
that later stops resolving: move it with § context-engine decision relink, and do not
hand-edit `code:`.

### context-engine decision relink

`decision relink <id> <old> <new>` replaces one `code:` link of a decision when the code it
names moves. Refuse, and write nothing, when:
- `<old>` and `<new>` are the same: nothing to do;
- `<new>` does not name code, as § context-engine decision link checks it: a blank, a directory
  or a path outside the repo is refused, so a dead link is never replaced by nothing;
- the decision is not a decision, or is `status: deprecated` (SUPERSEDED): its links are
  history, and G-T3 does not check them; link the code to the decision that replaced it (one
  `decision link <successor> <new>` per successor);
- `<old>` is not in its `code:`: if it is in another link field, that link is an id, and ids
  never move; otherwise name one of its `code:` links, or add one with `decision link`.

Re-read the file, then replace `<old>` with `<new>` in place in `code:` (if `<new>` is already
there, drop `<old>` and keep `<new>` once). The body and `body_sha` do not change. Log one
`relink` line with fields `["code"]`, then regenerate the index (§ context-engine decision
index). **Relink only to where the same behaviour now lives**, in the commit that moves it: if
what the code did is gone, the decision no longer describes the code, so supersede it.

**Why:** a moved file or renamed symbol leaves the link dead, G-T3 red and `why()` answering
from nothing. `code:` is written by an operation, so a hand edit would skip the existence check
and leave no op-log line. Whether the new code carries out the decision is a reading judgement
no operation can make (INV-15).

### context-engine decision find

A read. List the decisions matching every filter given: `--status` (case-insensitive),
`--tag`, `--links-to <target>` (as § context-engine why matches it) and `--text` (in the id,
title, description or body, case-insensitive). One line each by id:
`<id> <status> <title> (<actor>, <decided>)  [<tags>]`.

**Why:** "what did we decide about X" is answered by one-line rows, not by opening every file.

### context-engine decision show

A read. Print `<id> · <decision_status> · <title>`, then `actor`, `decided`, `session` and
every non-empty link field and `tags`, one per line, then the body, or only the
`## <section>` asked for (e.g. `Amendments`).

**Why:** one decision's status and links come first, so a reader rarely needs the whole file.

### context-engine decision index

Housekeeping (`hk_regen_index`). Rewrite `[working] decision_index` from the decisions'
frontmatter alone, never their prose:
1. `# Decisions`, a blank line, then the line
   ``Generated from each decision's frontmatter by `context-engine decision index`; never edit it by hand (G-D6).``
2. For each `decision_status` in the kind's enum order (then any other value, alphabetically)
   that has decisions: a blank line, `## <status>`.
3. Under it, group by each decision's first tag (`untagged` if none): tags alphabetical,
   `untagged` last. Per group: a blank line, `### <tag>`, a blank line, then one line per
   decision by id number:
   `- [<id>](<file name relative to the index>): <description, else title> *(<actor>, <decided>)*`,
   followed by `; superseded by <ids, comma-separated>` when `superseded_by` is set.
4. LF line endings and one final `\n`.

Lint G-D6 compares the file with a regeneration (line endings normalised), and fails a missing
index while any decision exists.

**Why:** an index built from frontmatter is checked by byte equality, so it cannot drift
quietly; one line per decision keeps it small as the series grows (FRAMEWORK §6.5).

### context-engine decision import

Turn a single-file decision log (FRAMEWORK §11.4) into one record per entry. Do it on a copy and
on a branch; nothing is written if any check fails.
1. The kind's `prefix` must be the log's (`D` for `D-n`), and no id in the log may already be a
   record.
2. Each entry starts at a heading `### <id> -- <title> *(<attribution>)*`, optionally followed
   by ` -- <note>` (`—` and `–` work as the dash), and runs to the next entry heading or the next
   `#` or `## ` heading. Its text is copied verbatim; an entry with no text stops the import.
3. Frontmatter: `title`; `actor`, the attribution up to its first comma or semicolon; `decided`,
   the last `YYYY-MM-DD` in it; `session`, the importing session; `decision_status: BUILT`
   unless the note says `SUPERSEDED by <id>`; `attribution`, the whole parenthetical, when it
   says more than `<actor>, <date>`; `imported_from`, the log's path.
4. The note: `SUPERSEDED by <id>`, `supersedes <id>`, `relaxes <id>`, `relaxed by <id>` and
   `narrowed by <id>` become links, written on both records (a link to an id not in the log
   stops the import); a SUPERSEDED record also gets `status: deprecated`. The note itself is
   kept as an amendment: `imported heading note: <note>`.
5. A `## ` section whose heading says "rejected" and holds a table: each row becomes a
   `decision_status: REJECTED` record with the next free id, in row order. Title: the first
   cell; body: the line *Imported from the table under*, the heading as `` `## <heading>` `` and
   a colon, then a blank line, the header line, the separator line and the row, verbatim;
   `actor: agent`; `decided`: the last date in the row's middle cells, else the date of the
   first entry its last cell names; `refs`: the entry ids in its last cell; `attribution`:
   which table, and where the reasoning is.
6. Stamp every record, log one `import` line each, and regenerate the index.

**Why:** "the import keeps every id", so `D-n` citations elsewhere still resolve; verbatim text
and a stamp make the move checkable line by line; all or nothing means a half-import never
lands. A rejected row becomes a record so "what was rejected that touches X" is a query.

### context-engine why

A read. The decisions whose link fields (and `answers`) name `<target>`: an id, a file, or a
`file::symbol`. A file matches its own `file::symbol` links, and a `file::symbol` matches a link
to the whole file. One line each by id, as § context-engine decision find, ending
`via <field, ...>`.

**Why:** "why is this code like this?" is answered by the decisions that link it, in one call,
instead of grepping a log.

## Bootstrap

### context-engine init

Give a repo the framework's files (FRAMEWORK §6.9). The kit is `src/context_engine/kit/` in the
engine repo at the pinned ref (or `context_engine/kit/` in the installed package), and its
`README.md` has the same steps.
1. If `context.toml` exists, keep it: check it loads (`context-engine lint` names what it
   refuses; stop and fix that first), and in steps 3 and 5 create only what it points at (a kind's
   `dir`, a `[working]` path, a route's `path`, the lock's directory).
2. Otherwise copy `context.toml.template` to `context.toml`; to change a kind's id prefix, edit
   `prefix` in its `[kinds.<name>]` table (no two kinds may share one, and none may collide with
   ids the repo already uses).
3. Copy `HANDOFF.md`, `docs/charter.md`, `docs/criteria.md`, `docs/ledger/session-log.md`,
   `docs/runbooks/manual-mode.md` and `docs/runbooks/rituals.md` from the kit to the same paths,
   skipping any that exist.
4. `CLAUDE.md`: if it holds no `<!-- context-engine kit <version> begin -->` marker, append the
   kit's `bootloader.md` after a blank line (create the file with a `# <repo>: contract` title if
   it is absent), keeping the file's line endings. If it holds an older version's block, or a
   block with no `@` import line (the inline block from before the bootloader), leave it for the
   upgrade to replace (kit README § Upgrade); never add a second block. Copy the kit's
   `contract.md` to `docs/framework/contract.md` if absent. If `.claude/settings.local.json` is
   absent, write it with the `SessionStart` hook from the kit README § Hook (this machine's
   absolute paths) and `.claude/.gitignore` holding `settings.local.json` if that is absent too.
   If it exists and has no such hook, it holds the owner's grants: show the owner the entry and
   ask; with a yes, add it to `hooks.SessionStart`, keeping every other key and its order (the
   engine's `--merge-settings`); with a no, leave it (`--skip-settings`).
5. For each of `docs/decisions`, `docs/stories`, `docs/working`, `docs/evidence` and `tasks`
   that does not exist, create it with an empty `.gitkeep`. Create
   `.context/.gitignore` and `.scratch/.gitignore`, each holding the line `*`, if absent.
6. Report in one line what you created and what you skipped. Never overwrite an existing file,
   and never install anything into the repo's environment.

**Why:** a new repo should get every file the rituals expect in one step, the two runbooks
included, so it can run every ritual by hand from its own tree, and an existing repo
must not lose a byte of what it has: it maps its components onto the routes instead of moving
them (FRAMEWORK §11.4). The engine also refuses a file that appears while it runs (it creates
each one only if it is still absent) and a `CLAUDE.md` that changed since it read it; by hand,
`git status` before committing shows the same.
