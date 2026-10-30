# Criteria

LIVING. The definition of correct for the engine (FRAMEWORK §3.3). The engine is a library, so
the criteria are properties, checked by pytest. **A test claims a criterion with
`@pytest.mark.criterion("AC-n")`** (the marker is registered in `pyproject.toml`); the
engine's lint checks the chain (CE-25): G-T2 checks that every `tested` criterion is claimed and
every claim resolves, G-T6 that every `from` names a story or decision, and G-T1 that every live
story has a row here. A criterion's actor is its source's. Not every test needs to name a criterion. **A criterion becomes `tested` only after its claiming
test has been sabotaged red** (DEC-11, `CLAUDE.md § Sabotage rule`).

Statuses: `planned` (no test yet) · `tested` (a claiming test exists) · `manual` ·
`deviates` · `retired` (FRAMEWORK §3.3). Drafted by the agent on 2026-10-08 from the stories;
live by default under "inform and proceed" (FRAMEWORK §3.3). Ids are never reused (P3).

## Core (CE-1)

| id | criterion | from | status |
|---|---|---|---|
| AC-1 | Reading a record and writing it back unchanged is byte-identical, including unknown keys, key order and comments | US-6, US-2 | tested |
| AC-2 | Unknown frontmatter keys survive every engine write (OKF §4.1) | US-6 | tested |
| AC-3 | Every record the engine writes has a non-empty `type`; a `.md` in a configured bundle directory without one is a lint failure (G-D11) | US-2 | tested |
| AC-4 | Ids are allocated by scanning every record of the series, open and closed, and are never reused; two concurrent allocations never return the same id (G-D2) | US-2 | tested |
| AC-5 | A write that breaks its kind's schema is refused before any byte is written, and the refusal names the remedy (P7) | US-2 | tested |
| AC-6 | Every write appends an operation-log entry carrying the session key and the actor; `--mechanical` writes are marked as such | US-3 | tested |
| AC-7 | `body_sha` normalises line endings: one record checked out with LF and with CRLF hashes the same (spike finding) | US-7 | tested |
| AC-8 | Changing an append-only record's body above `## Amendments` fails lint (G-D10); an `amend` operation passes | US-7 | tested |
| AC-9 | Two processes writing different records at once both succeed; two writing the same record are serialised by the lock and neither write is lost (P12) | US-2 | tested |

## Working state (CE-2)

| id | criterion | from | status |
|---|---|---|---|
| AC-10 | `session.start` mints `max(newest ledger key, banner key) + 1 letter` under the lock and writes a `kind: open` stub; two concurrent starts get different keys (FRAMEWORK §5.5) | US-8 | tested |
| AC-11 | `session.close` refuses a malformed receipt and finalises the session's stub; `session.pause` writes `kind: pause` | US-8 | tested |
| AC-12 | Closing a task sets `state: closed` and derives `status: deprecated` in place; the file's path does not change; a close without a message is refused | US-5 | tested |
| AC-13 | Listing filters and sorts by state, priority and label without reading bodies, one line per record | US-5, US-1 | tested |
| AC-14 | `pause.open` records the branch and uncommitted paths from git itself and commits its own record by path | US-8 | tested |
| AC-15 | A baton older than two sessions is reported by lint (G-W3) and converted into a task by housekeeping | US-8, US-3 | tested |
| AC-16 | `banner.set(text, seen_hash)` refuses when the banner has changed since `seen_hash` | US-8 | tested |
| AC-17 | `orient()` stays under its configured size cap and contains: the banner, open batons and pause records (own first), other open sessions, the NEXT tier, overdue owner questions, and the top item's brief, Traps and Read first | US-1 | tested |
| AC-55 | Taking an item off NOW (`task close`, `ask answer` on a question at NOW, or `task promote` to a lower tier) while other items stay open and NOW falls below its cap succeeds and its one-line reply says G-W5 is red, with G-W5's own message, and asks the owner which item to `task promote <id> NOW`, naming the NEXT items or saying NEXT is empty; it promotes nothing. Such an op says nothing of G-W5 when it leaves NOW at or over its cap, leaves nothing open, moves an item not at NOW, or G-W5 is off in `[guards] off` (CE-36) | US-5 | tested |

## MCP (CE-3)

| id | criterion | from | status |
|---|---|---|---|
| AC-18 | Every MCP tool calls the same function as its CLI subcommand; there is one implementation per operation | US-4 | tested |
| AC-19 | Every write tool returns one line; every read tool returns a capped slice with a pointer to the rest | US-1 | tested |
| AC-20 | `hk.close` refuses unless the named commit really carries `Closes: <id>` or the session's ledger entry names the item (G-W9) | US-3 | planned |

## Manual mode (CE-8)

| id | criterion | from | status |
|---|---|---|---|
| AC-21 | Every `context-engine` subcommand has a `### context-engine <group> <op>` section in `docs/runbooks/manual-mode.md` giving its by-hand steps and a **Why** | US-11 | tested |
| AC-22 | `context-engine record stamp` checks every named id before stamping any (all or nothing) and never replaces a stamp; `context-engine record amend` appends under `## Amendments` and refuses a body that moved since its stamp | US-7, US-11 | tested |
| AC-23 | This repo's own records pass `context-engine lint` with no failures: every decision and story stamped and unchanged since, every board item in schema, the working-state guards green | US-7 | tested |
| AC-24 | The routing table is `[[routes]]` in `context.toml`: `context-engine routes` prints it, a route missing `component`, `path` or `mode` or carrying an unknown key is refused at load, and lint fails (G-R1) when a non-optional routed path does not exist | US-9 | tested |
| AC-25 | `context-engine record new` writes a decision or story stamped when it is created, fills a missing required key only when it can mean nothing but now (a date with today, a session key with this session), never guesses `actor`, and refuses a non-append-only kind | US-7, US-11 | tested |

## Design review and the residual-risk register (CE-23)

| id | criterion | from | status |
|---|---|---|---|
| AC-26 | `task promote <id> NOW` on an item carrying `review:` is refused, naming every reason, while its `## Design review` is missing, still the template, lacks `affects:`, a risk line, a rung, a residual's `why:` or `control:`, or an F, A, M or E line; an item with no `review:`, or a promotion below NOW, is not checked; a `review:` value outside `[working] review_triggers` is refused | US-14 | tested |
| AC-27 | `task close` on an item carrying `review:` appends each residual to the configured register as the next `INV-n`, under the close's lock, and logs it; re-closing adds no duplicate; it refuses residuals with no register configured, and a review that is not ready | US-14 | tested |
| AC-28 | Lint fails G-W12 on an open NOW item carrying `review:` whose review is not ready, and G-W13 on a closed reviewed item whose residuals are missing from the register, a register entry missing a field, or two entries sharing an INV id | US-14 | tested |
| AC-29 | The engine's register ships as package data: `register show --engine` reads the `REGISTER.md` inside the installed package, and `orient` in a repo whose register is not that file points at it | US-14 | tested |

## Adoption (CE-15)

| id | criterion | from | status |
|---|---|---|---|
| AC-30 | `context-engine init` (CLI and MCP, no `context.toml` needed) writes the adoption kit into an empty repo, and that repo then passes `context-engine lint` and runs `session start`, `session close` and its first `banner set` with no hand edit | US-9 | tested |
| AC-31 | `init` only creates: a file that exists is byte-identical afterwards, `CLAUDE.md` gets the marked kit block appended only when its markers are absent (keeping its line endings), the repo's `.gitignore` gets `.context-engine/` appended (or is created holding it) only when no line ignores it (keeping its line endings, refusing one edited after the plan, and leaving a non-UTF-8 one with a warning; DEC-41), a second run creates nothing, and a different `context.toml` or a bad or colliding `--prefix` is refused | US-9 | tested |
| AC-32 | The kit's `context.toml.template` is the config schema: it sets every key the engine reads and parses as a config, every tuned value in it carries a provenance note, and loading a config refuses an unknown key in `[engine]`, `[working]` or `[kinds.*]`, naming the allowed keys | US-15 | tested |
| AC-33 | The kit's contract carries FRAMEWORK §6.6 'Ultracode', 'The coordinator' and the fable rule verbatim and a `framework:` pin, and the kit block is marked, pins the engine's major.minor and imports the contract, and neither the kit nor FRAMEWORK carries this repo's ids (other than `(CE-n)` build marks) or paths | US-9, US-15 | tested |
| AC-34 | `banner show` on an orientation note with no banner gives hash `none`; `banner set --seen none` writes the first banner just before the orientation note's first `## ` section (creating the orientation note if absent), and refuses any other hash while there is no banner | US-15 | tested |

## Versioning (CE-21)

| id | criterion | from | status |
|---|---|---|---|
| AC-35 | Lint fails G-D0, naming the remedy, when the contract (`[engine] contract`, default `CLAUDE.md`) is missing, has no `framework:` line, has one that is not `major.minor` or `major.minor.*`, has one whose major.minor differs from the installed engine's, or holds a kit block whose begin marker names another version (the kit block half is AC-58); `0.5` and `0.5.*` both pass against any engine `0.5.N` (DEC-23) | US-9 | tested |

## Kit block (CE-38)

| id | criterion | from | status |
|---|---|---|---|
| AC-57 | `init` writes the kit block into `CLAUDE.md` (as AC-31), the kit's contract to docs/framework/contract.md (in the target repo), and, only when `.claude/settings.local.json` is absent, that file holding one `SessionStart` hook with no matcher whose command, run through a shell from another directory with no `CE_` variables, prints `orient`, plus `.claude/.gitignore` ignoring it; an existing settings file without the hook makes `init` (dry run too) refuse, naming the one entry it would add and both flags, writing nothing; `--skip-settings` leaves it byte-identical; `--merge-settings` appends only that entry to `hooks.SessionStart`, keeping every other key, their order, its line endings and non-ASCII text, refuses untouched (before any write) a file that is not strict JSON (a repeated key, `NaN`, `Infinity`, an overflowing number or a lone surrogate included), not that shape, setting `disableAllHooks`, hard-linked or read-only, or running orient with another command (or only under a matcher), refuses one that changed after the plan, and is a no-op once the hook is there; a hard-linked `CLAUDE.md` stays linked; a CLI refusal is UTF-8 on stderr; and a current-version inline kit block is left as it is and named as the upgrade | US-17 | tested |
| AC-58 | Lint fails G-D0, naming the remedy, when the contract's kit block of the engine's version is not the kit block text the kit ships (an inline block, a hand edit, or no end marker), when a file it `@`-imports (resolved against the contract's own directory) is missing, or when that file is not the installed engine's `src/context_engine/kit/contract.md`, line endings aside | US-17 | tested |
| AC-59 | `orient` opens with a `Contract: fix this first` section listing every G-D0 failure with its remedy, and has no such section when G-D0 is green or `[guards] off` names it | US-17 | tested |

## Procedures runbook (CE-24)

| id | criterion | from | status |
|---|---|---|---|
| AC-36 | Every FRAMEWORK §6 subsection has a row in `docs/runbooks/procedures.md`'s map naming its procedure sections, or saying it has no steps; every step row of a procedure names only existing `context-engine` operations, links each one's manual-mode section, resolves every `§` reference and has a Why; and every §6 item number a step is labelled with exists in that subsection (P3) | US-15, US-11 | tested |
| AC-37 | The kit ships `docs/runbooks/procedures.md` and `docs/runbooks/manual-mode.md`, byte-equal to this repo's; `init` copies them and keeps a copy the repo already has; a wheel built from the source carries every kit file | US-15 | tested |

## Decision records (CE-5)

| id | criterion | from | status |
|---|---|---|---|
| AC-38 | `record correct` inserts `[text]` right after the one place its one-line anchor occurs in a stamped append-only record (decision or story), keeps `body_sha` (it pins the words as typed) and logs a `corrected:` amendment saying where; undoing the logged insertions newest first gives back the original body byte for byte, also for an insertion inside an earlier one; a missing or repeated anchor, a multi-line or empty text, a body changed since its stamp and a board record are refused with nothing written; lint G-D10 fails a record whose `corrected:` lines do not match its body, and one whose body with its logged insertions undone does not hash to `body_sha` (a dropped `corrected:` line, a hand re-stamp) (DEC-13) | US-7 | tested |
| AC-39 | `decision supersede <old> <new>` writes `superseded_by` on the old and `supersedes` on the new under one lock, and sets the old's `decision_status: SUPERSEDED` and OKF `status: deprecated`; it refuses a decision superseding itself, a repeat, and a SUPERSEDED or REJECTED replacement; `decision link --rel relaxes` writes the `narrowed_by` backlink | US-7 | tested |
| AC-40 | `decision link` puts a board id in `tasks` and a `file::symbol` in `code` unless `--rel` says otherwise, and refuses a record id that does not exist, a criterion id that is not a row of `[working] criteria`, an id of no record kind, a file that does not exist case-exact, a code link that names no repo file (blank, a directory, outside the repo, written with `\`) or has an empty symbol part, a symbol the file does not name, a duplicate, and a target it cannot place; `why(target)` lists exactly the decisions whose links name the target, with the field, a file matching its own `file::symbol` links and the reverse; `decision find` filters by status, tag, link and text; `decision show` gives one section | US-7, US-1 | tested |
| AC-41 | With `[working] decision_index` set, every decision write (new, amend, correct, supersede, link, `ask answer`) regenerates the index from frontmatter, grouped by status in the kind's enum order, then by first tag with `untagged` last, one line per decision; lint G-D6 fails a hand-edited index, and a missing one while any decision exists, until `decision index` regenerates it | US-7 | tested |
| AC-42 | `decision import` writes one stamped record per `### D-n -- title *(actor, date)*` entry with its id, title, actor and date kept and its text verbatim, the heading's trailing note as links on both records plus an amendment, and each row of the "rejected" table as a REJECTED record with a new id; an id in another prefix is renamed to the kind's prefix, keeping its number, with the old id kept as an alias (DEC-37, DEC-40); it writes nothing when an id repeats or is in use, a heading or table row does not parse, a note links an id not in the log, or a later record breaks the schema; `--dry-run` writes nothing | US-7 | tested |
| AC-53 | `decision set` changes only a decision's own frontmatter (`decision_status`, `reopen_if`, `tags`, ...), logs `set` and regenerates the index, leaving the body and `body_sha` untouched; it refuses, writing nothing, `type`, `id`, `body_sha`, `status`, `answers`, the provenance keys (`actor`, `ruled_by`, `decided`, `session`, `attribution`, `imported_from`, `generated`), `verified` and every link field (set or unset), `decision_status: SUPERSEDED`, any `decision_status` change on a SUPERSEDED decision, `reopen_if` on a decision that would not be REJECTED, and a record that is not a decision; each refusal's remedy is a command that works (CE-32) | US-7 | tested |
| AC-54 | `decision relink <id> <old> <new>` replaces one `code:` link of a decision in place (an `<old>` whose `<new>` is already linked is dropped, `<new>` kept once), logs `relink` with fields `["code"]`, and leaves the body and `body_sha` untouched; it refuses, writing nothing, `<new>` equal to `<old>`, a `<new>` that does not exist case-exact, names no repo file (blank, a directory, outside the repo) or whose symbol the file does not name, an `<old>` not in `code:` (naming the field when it is an id link), a superseded decision (naming one `decision link` per successor) and a record that is not a decision; G-T3's remedy for a dead `code:` link is a `decision relink` that turns it green (CE-35) | US-7 | tested |
| AC-98 | `ask answer` with a ruling and `ruled_by` (CLI `--ruling`/`--ruling-file`, `--ruled-by`) records a decision with `actor: owner asked` and `ruled_by`, the owner's delegating words alone inside the owner quote and the ruling under `## Ruling` outside it, `ruled_by` in the question's `answered:` and log line, and `ruled by` in the index line; it refuses, before any byte, a ruling without `ruled_by`, `ruled_by` without a ruling, `ruled_by: owner`, and owner words holding a `## Ruling` heading (CE-113) | US-7 | tested |
| AC-99 | `record new` of a decision refuses, before any byte, a `ruled_by` that is blank or `owner`, a decision with `ruled_by` whose `actor` is `owner` or `human:<id>` alone, whose body has no `## Ruling` section, nothing above it or an empty one, and a `## Ruling` section with no `ruled_by`, its remedy naming `ruled_by` and `## Ruling`; a well-formed delegated ruling is created and stamped; `decision set` refuses `ruled_by` (CE-113) | US-7 | tested |
| AC-100 | G-I3 fails a current decision whose hand-edited frontmatter breaks AC-99's rules (`actor: owner` on a delegated ruling, a blank or dropped `ruled_by`, `ruled_by` with no `## Ruling` section), its remedy naming `record new decision` then `decision supersede`; following it clears the failure, and a superseded decision is not read (CE-113) | US-7 | tested |
| AC-101 | `record new` of a decision and `ask answer` refuse, before any byte, a `ruled_by` or a lone `actor` that names the owner in any case (`Owner`, `OWNER`, `Human:<id>`), and a decision text holding a `## Amendments` line (in the owner's words or in the ruling, delegated or not), which would put the text below it outside `body_sha` as a later amendment, their remedies naming `record amend`; G-I3 fails a hand-edited `ruled_by: Owner` or `actor: Owner` on a delegated ruling (CE-138) | US-7 | tested |

## Guard catalogue (CE-14)

| id | criterion | from | status |
|---|---|---|---|
| AC-43 | `[guards] off` drops exactly the guard ids it names from lint (and from `lint --working`); an id lint does not report, and an unknown `[guards]` key, are refused when the config loads with the allowed ids as the remedy; a path a `[guards]` list names that does not exist is a failure of that guard (FRAMEWORK §8.0) | US-2 | tested |
| AC-44 | G-D1 fails a routed file, or any `.md` under a routed directory at any depth, over its route's `max_lines`, `max_bytes` or `max_width` (table rows exempt from width); a route with no caps is not checked | US-2 | tested |
| AC-45 | G-D2 fails two files of one series carrying the same id, by file name or by `id:`, and an id the op log shows created twice | US-2 | tested |
| AC-46 | G-D3 fails, in the docs `[guards] links` lists, a relative link or reference definition to a missing path or a path of the wrong case, an `#anchor` naming no heading of the target, and a backticked `file::symbol` whose file is missing (case-exact; a bare name may be anywhere) or does not name each dotted part; URLs, inline code that is not `file::symbol`, fenced code and records with `status: deprecated` are not checked | US-2 | tested |
| AC-47 | G-T3 fails, in the docs `[guards] existence` lists, a backticked file name or `file::symbol` that does not exist; blockquotes, frontmatter and lines marked `*HISTORY —*` are exempt, and spans with spaces, globs, placeholders or a leading `.` or `/` are not names; it also fails a `code:` link of a decision that is not `status: deprecated` whose file or symbol no longer exists, or that names no repo file by the rule `decision link` applies | US-2 | tested |
| AC-48 | G-D7 fails a doc in `[guards] signals` with more ⚠ than `warn_max`, more bold all-caps spans than `bold_caps_max`, or any `retired_glyphs` glyph; fenced code is not counted | US-2 | tested |
| AC-49 | G-D8 fails an orientation note with two banner headings, any other heading carrying a session key (a pasted ledger entry included), or a banner bullet or bold lead that is a session key; a wrapped line and dated facts outside the banner pass | US-2 | tested |
| AC-50 | G-D9 fails each number `context.toml` assigns (inline tables included, strings ignored) whose line has no `provenance: MEASURED` or `JUDGEMENT` note, no `wrong if`/`wrong as above`, or cites an example; the kit's template passes it | US-2 | tested |
| AC-51 | G-W7 fails a board item whose `moved`, `updated`, `closed` or `last_asked` differs from the session of the newest logged operation that wrote that key, a value no logged operation wrote unless it predates the log, and an op log line that does not parse | US-2 | tested |
| AC-52 | `orient`'s other-open-sessions section is headed as an instruction to show the owner each one, one line each; it lists every other `kind: open` stub with when it opened and when it last did anything (its newest op log line or `Session:`-trailered commit), never the session's own, and says `none` when there are none | US-16 | tested |
| AC-88 | `session abandon` marks another session's `kind: open` stub `kind: abandoned`, its lines kept and an `abandoned:` line added naming the abandoning session, the stub's last activity and the closes or pauses since; it refuses the session's own key, a stub that is not `kind: open`, and one with fewer closes or pauses since its last activity than the window (DEC-29) unless `--force` (the owner's word); `--stale` abandons every other stub past the window and refuses `--force`; any activity resets the window, an op line by its position in the op log and a commit by the op log it carries, never by its date (CE-129); a stub with neither counts from when it opened; its one baton names the stub's uncommitted op lines and the open board items whose `updated` or `moved` names it (CE-131) | DEC-69 | tested |
| AC-89 | `session start` warns, naming the spelling and its op line count, when the op log already signs the same agent another way: the same harness, and models equal once lowercased, `.` and `_` read as `-` and a leading `claude-` dropped, or one model a dash-prefix of the other (a bare tier and a versioned id); the most used spelling first, and nothing for a `human:` or `process:` actor, another harness or another model (CE-122) | US-8 | tested |
| AC-90 | Orient lists each ACTIVE-PLAN doc G-D4 reads whose named board items are all closed (a close by hand skips `task close`'s check), with `doc freeze`, or for a doc `[guards] liveness_given` declares, its context.toml entry; nothing while one item is open, after the freeze, or with G-D4 off (CE-97) | DEC-19 | tested |
| AC-91 | Orient lists each open NOW or NEXT item, and each board id a banner line holding the word "next" names, whose `deps` include an open SOMEDAY item, naming the parked dep; a dep open at LATER is not flagged, and promoting the dep clears the line (CE-116) | US-8 | tested |
| AC-92 | With `[guards] stories` set, orient lists each `unspecified` story with the open board items that name it as a whole word (the ones G-T1 counts), or says none does; closed items and longer ids (`US-40`, `XUS-4`) do not count (CE-48) | US-2 | tested |
| AC-93 | With an upstream branch, orient says how far HEAD is ahead of and behind it, and flags the upstream's newest `update by push` reflog entry when it falls in no session's window in the op log (its `session.start` to its close, pause or abandon); nothing without git or an upstream (CE-114) | US-8 | tested |
| AC-94 | Orient lists the foreign commits of the session's own range (`ledger.foreign_commits`) and of the newest abandoned sessions' ranges, each named by short hash, subject, author and whose range it is (CE-101) | US-8 | tested |
| AC-95 | G-D0 fails a contract that still holds a `<...>` placeholder of the kit's Gate stub (read from `src/context_engine/kit/bootloader.md`, after its end marker), its remedy naming kit README § 2a step 2; replacing it clears the failure (CE-71) | US-9 | tested |
| AC-96 | Orient lists the charter and criteria file (their configured paths, else the kit's) while each equals the kit's template, or still holds one of its `*(...)*` placeholders, naming the ones left; filled, nothing; lint does not fail them (CE-121) | US-9 | tested |
| AC-97 | In a repo with this engine's kit block, G-D0 fails each runbook the installed kit ships (`bootstrap.FILES` under `docs/runbooks/`) that is missing from the repo or that no route covers (its path or a directory above it), its remedy naming kit README § 4 step 2; a contract with no kit block is not checked (CE-50) | US-9 | tested |
| AC-56 | G-D12 (CE-30) fails each component of §2's table, `§5.6`/`§6.n` procedure heading and G-id the `[guards] coverage_spec` names, outside fenced code, that no table row of the newest `[guards] coverage_maps` map (by the date and session letters in its file name, ordered as session keys: `z` before `aa`) names in its class's key column (`Component`; `§` in a table with a `Ritual` or `Procedure` column; `Guard`; only a component's cell may add ` (...)`) and no board item, open or closed, names as a whole word (`XG-D7` and `G-D70` do not name G-D7, nor are `XG-D99` and `G-D98x` G-ids in the spec); it fails a class extracted under its floor (its remedy naming how a repo switches G-D12 off), one of the two keys set without the other, a missing spec, a glob that is absolute or has a `..`, a glob matching nothing and a matching map with no date, and is off while neither key is set | US-2 | tested |
| AC-74 | G-D4 fails a doc under `[guards] liveness` or `history` that declares no liveness in its first `liveness_lines` lines (a frontmatter `liveness:` key, or a line opening a block led by LIVING, ACTIVE-PLAN or FROZEN, or `ARCHIVED <date>`, after a blockquote's `>` and emphasis; the word mid-line, on a wrapped line or in fenced code declares nothing) and that no `liveness_given` glob covers; a frontmatter `liveness:` that is not a liveness word; a doc contradicting its `liveness_given` entry; a glob matching no file; a LIVING doc in a history directory; an ACTIVE-PLAN doc naming no board item near its top, or only closed ones; a missing path; and a `liveness` list holding no doc | US-2 | tested |
| AC-75 | G-D5 fails, in the docs `[guards] numbers` lists, a number (a numeral, or spelled from three to twenty, not glued to a token on its left) directly before a `count_nouns` noun in prose, in any case; fenced code and frontmatter, backticked or double-quoted spans, lines with a `YYYY-MM-DD` anywhere, bounds (`at most N`) and FROZEN or ACTIVE-PLAN docs pass, and a missing path or a list of only those docs is red | US-2 | tested |

## Correctness chain (CE-25)

| id | criterion | from | status |
|---|---|---|---|
| AC-65 | With `[guards] charter` and `stories` set, G-I1 fails a charter goal no story that is not retired names, a story naming no goal or a goal the charter lacks (a legacy `G3` reads as `G-3`), a charter goal id not in the `G-n` form or leading two rows, a missing charter, a charter with no row led by a goal id and a row of the goal table not led by one; it is off while `charter` is unset, and red when `charter` is set without `stories` | US-2, DEC-33 | tested |
| AC-66 | G-I2 fails a story that is not retired whose actor is not `owner`, `human:<id>` or `agent (reconstructed from ...)`, whose date is not a date, whose `story_status` is outside live, unspecified, unconfirmed, retired, or that is `unconfirmed` without an agent's actor; `record new` of a story refuses each of those, and a goal the charter lacks or not in the `G-n` form, by the same checks, writing nothing | US-2, DEC-33 | tested |
| AC-67 | G-T1 fails a live story that is the `from` of no criterion row that is not retired, and an unspecified story that no open board item names as a whole word | US-2 | tested |
| AC-68 | G-T2 fails a `tested` or `manual` criterion that no claim under `[guards] tests` names, a claim naming no row, and a status outside the vocabulary; the `[guards] claim` pattern defaults to a pytest `criterion("AC-n")` marker or a `criterion: AC-n` comment, and one without exactly one group is refused when the config loads | US-2 | tested |
| AC-69 | G-T6 fails a criterion whose `from` cell names no id, or an id that is neither a story nor a decision record | US-2, DEC-33 | tested |
| AC-70 | G-T1, G-T2 and G-T6 each fail a missing criteria file, a table of criteria with no `status` or source column, a file with no row led by an id, and a row of a table of criteria not led by a plain id (an id in the stored file is read as written, `AC-05`, and a GFM-escaped `\|` stays in its cell); G-T2 fails a `[guards] tests` path that does not exist, `tests` set without a criteria file, and a claim pattern that matches nothing; each is off while a source it needs is unset | US-2 | tested |
| AC-72 | `record retire` retires a story in one write, all checked before any byte: `story_status: retired`, `status: deprecated`, `superseded_by` on it and `supersedes` on its successor (written first, so a retry completes a failed write), the reason as an amendment, one `retire` op log line per record, committed by path through the CLI (a `--file` read without its BOM) and the MCP tool alike; `by` is `owner` or `human:<id>` (the words are theirs) or `agent`, which needs a successor carrying the story's words as typed; it refuses a successor that is not a story, is the story or is retired, a story whose hash does not match, and a story that a logged `retire` retired, even after a hand edit undid it; `record new` refuses a story created as `retired`, `status: deprecated` or with a story link | US-7, US-2 | tested |
| AC-73 | G-I2 fails a story marked retired that no logged `retire` retired, a story that a logged `retire` retired but that is no longer `retired` with `status: deprecated`, a story that is `status: deprecated` but not retired, a `superseded_by` or `supersedes` naming no story, and `superseded_by` on a story that is not retired; it reads no provenance of a retired story, so the G-I1 and G-I2 remedies name `record retire` and following them clears the failure; G-T1's remedy, for a live story that replaced a story some criteria cite as their source, says to add the new story to those criteria's `from` cells | US-2 | tested |
| AC-84 | `record confirm` moves a story an agent reconstructed from `unconfirmed` to `live` (or `unspecified`) in one write: `story_status`, the confirmer's words verbatim as an amendment (`confirmed (by <who>): ...`), one `confirm` op log line, the `actor` kept, committed by path through the CLI (a `--file` read without its BOM) and the MCP tool alike; `by` is `owner` or `human:<id>`, never an agent; it refuses, before any byte, a record that is not a story, an owner's story, a retired story, a story whose hash does not match, and a story that a logged `confirm` confirmed, even after a hand edit undid it; `record new` refuses a reconstruction created `live` or `unspecified` | US-2 | tested |
| AC-85 | G-I2 fails a story that is not retired, has an agent's actor and is `live` or `unspecified` with no logged `confirm`, and a story that a logged `confirm` confirmed but that is `unconfirmed` again; its remedy names `record confirm`, and following it clears the failure | US-2 | tested |
| AC-86 | With `[guards] task_goals` naming the task kind (and `charter` set), G-I1 fails an open task whose `goals` is empty, names a goal the charter lacks, or is not in the standard `G-n` form; closed tasks are not read, and `task_goals` without `charter` is red. `task new --goals` and `task set` refuse the same before any byte is written, and `task reopen` refuses a closed task that would reopen failing it (CE-103) | DEC-64 | tested |
| AC-87 | Orient says "rerank due" with its reason, and never runs the rerank, only when NEXT holds no task while tasks are open: what NOW holds does not matter, owner questions do not count, and the charter's `Last rerank:` line (with `[guards] charter` set) is quoted after the reason, never a trigger (DEC-64, amendment 2026-10-20f) | DEC-64 | tested |

## Method runbooks (CE-26)

| id | criterion | from | status |
|---|---|---|---|
| AC-71 | The kit ships the method runbooks FRAMEWORK §7.5 names (`gate.md`, `sabotage.md`, `fan-out.md`, `release.md`), byte-equal to this repo's, and `init` copies them; §7.5 names every runbook the kit ships and the kit ships every runbook §7.5 names; each method runbook declares `mode` and `liveness` (LIVING, ACTIVE-PLAN or FROZEN) in its frontmatter, and has its own `[[routes]]` entry with G-D1 caps both here and in the kit's config template, so an adopted repo that loses one fails lint G-R1 and one that outgrows its cap fails G-D1; and `fan-out.md`'s build rounds are FRAMEWORK §6.6's steps, in its order and with its numbers | US-9, US-15 | tested |
| AC-110 | The kit README's MCP-registration section names the connect timeout: Claude Code gives the server 30 seconds, it has taken 33 to 36 under load, and `MCP_TIMEOUT` (milliseconds) is the remedy (CE-85) | US-9 | tested |

## Commits at milestones (CE-55)

| id | criterion | from | status |
|---|---|---|---|
| AC-76 | `[engine] commit` is `milestones` (the default), `every-write` or `off` (an older `true` reads as `milestones`, `false` as `off`, anything else refuses); under `milestones` exactly task close, record new, amend and retire, decision supersede, ask answer, baton add, pause open, session close and pause, and banner set commit, each carrying every op log line HEAD lacks with the files they name, and every other write commits nothing | DEC-36 | tested |
| AC-77 | A task close's commit is titled `<id>: close; <message>` (cut to 72 characters, the whole message then in the body), carries the close's optional body and `Closes: <id>` with `Session: <key>` in its trailer paragraph, and a close refused after its write commits that write without `Closes:` | DEC-36 | tested |
| AC-78 | `context-engine commit [paths] -m ...` (and the MCP tool) commits the paths by path with every op log line HEAD lacks and the files they name, whatever the policy, adds a `Session:` trailer where git reads it, keeps what other sessions staged or left untracked as it was, and refuses (committing nothing, taking back any add) a missing message, another session's trailer, the whole repo, pathspec magic, an ignored path, nothing to commit, a path git does not know, and a root not inside a git work tree | DEC-36 | tested |

## CI parity (CE-67)

| id | criterion | from | status |
|---|---|---|---|
| AC-79 | `tools/linux_gate.py [rev]` runs CI's gate job on any commit, pushed or not, in a Linux container on the owner's machine, set up like CI's runner (`ubuntu-latest`'s Ubuntu, git from the git-core PPA with the runner image's `safe.directory = *`, uid 1001, Python at the `requires-python` floor): a fresh clone of that commit, the workflow's install step, then its gate, exiting with the gate's status and naming the git and Python it ran; its steps match the workflow's | US-18 | tested |
| AC-80 | No test's result depends on the machine's git config or on platform-specific standard-library internals: git in a test reads no system or global config, and no test patches an attribute of a standard-library module | US-18 | tested |

## Freeze and archive (CE-27)

| id | criterion | from | status |
|---|---|---|---|
| AC-81 | `doc freeze` writes `FROZEN <date> (session <key>): <why>` and a blank line above a doc's topmost liveness declaration as G-D4 reads it, keeping every other byte (a BOM, the line endings) and wrapping the line at 100 characters, and logs `doc.freeze`; it refuses, writing nothing, a doc already FROZEN, one with no declaration in the window, one declared by a frontmatter key or by `liveness_given`, a record, a file that is not `.md` and a path outside the root | US-9 | tested |
| AC-82 | `task close` refuses, before any byte, to close the last open board item that an ACTIVE-PLAN doc G-D4 reads names in its window, naming each such doc with `doc freeze <doc>` as the remedy; once they are frozen the close goes through and G-D4 stays green; with G-D4 off it does not check | US-9 | tested |
| AC-83 | `doc archive` moves a tracked, committed `.md` doc without frontmatter into `--to` or `[working] archive`, its first line `ARCHIVED <date> (session <key>), from <old path>.` and the rest unchanged; adds its row to that directory's `README.md` redirect table (made LIVING by the first archive, or a `## Redirects` section in a README without one); logs three `doc.archive` lines and stages nothing, so the next commit carries a rename; names a `context.toml` entry left on the old path; and refuses, writing nothing, an untracked doc, uncommitted changes, frontmatter, a name already archived there, a doc already in the directory or named `README.md`, a directory outside the root, and no directory | US-9 | tested |

## Drafted for live stories that had no criteria (CE-25, DEC-33)

Planned, drafted by the agent from each story's own words so G-T1 lands green; the owner may push
back through the digest (FRAMEWORK §3.3).

| id | criterion | from | status |
|---|---|---|---|
| AC-60 | A long gate phase can be split into parts run separately (in parallel where they allow it), and each part's result is recorded against a hash of the code it tests | US-10 | planned |
| AC-61 | A new session can tell which parts are already tested for the current code and which are not, without re-running them | US-10 | planned |
| AC-62 | A session can leave a short after-action review (what worked well, what could be improved), kept where a later stocktake of the framework finds every one | US-12 | planned |
| AC-63 | Besides a clean close, a session can be rolled back and closed: what it changed is undone and the session ends | US-13 | planned |
| AC-64 | Rolling a session back leaves the work of other humans and agents in the same checkout (a shared directory, not a worktree) untouched | US-13 | planned |
