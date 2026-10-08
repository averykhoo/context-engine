# Criteria

LIVING. The definition of correct for the engine (FRAMEWORK §3.3). The engine is a library, so
the criteria are properties, checked by pytest. **A test claims a criterion with
`@pytest.mark.criterion("AC-n")`** (the marker is registered in `pyproject.toml`); once the
engine exists, G-T2 checks that every `tested` criterion is claimed and every claim resolves.
Not every test needs to name a criterion. **A criterion becomes `tested` only after its claiming
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
| AC-17 | `orient()` stays under its configured size cap and contains: the banner, open batons and pauses (own first), other open sessions, the NEXT tier, overdue owner questions, and the top item's brief, Traps and Read first | US-1 | tested |

## MCP (CE-3)

| id | criterion | from | status |
|---|---|---|---|
| AC-18 | Every MCP tool calls the same function as its CLI subcommand; there is one implementation per operation | US-4 | planned |
| AC-19 | Every write tool returns one line; every read tool returns a capped slice with a pointer to the rest | US-1 | planned |
| AC-20 | `hk.close` refuses unless the named commit really carries `Closes: <id>` or the session's ledger entry names the item (G-W9) | US-3 | planned |

## Manual mode (CE-8)

| id | criterion | from | status |
|---|---|---|---|
| AC-21 | Every `context-engine` subcommand has a `### context-engine <group> <op>` section in `docs/runbooks/manual-mode.md` giving its by-hand steps and a **Why** | US-11 | tested |
| AC-22 | `context-engine record stamp` checks every named id before stamping any (all or nothing) and never replaces a stamp; `context-engine record amend` appends under `## Amendments` and refuses a body that moved since its stamp | US-7, US-11 | tested |
| AC-23 | This repo's own records pass `context-engine lint` with no failures: every decision and story stamped and unchanged since, every board item in schema, the working-state guards green | US-7 | tested |
| AC-24 | The routing table is `[[routes]]` in `context.toml`: `context-engine routes` prints it, a route missing `component`, `path` or `mode` or carrying an unknown key is refused at load, and lint fails (G-R1) when a non-optional routed path does not exist | US-9 | tested |
| AC-25 | `context-engine record new` writes a decision or story stamped at birth, fills a missing required key only when it can mean nothing but now (a date with today, a session key with this session), never guesses `actor`, and refuses a non-append-only kind | US-7, US-11 | tested |
