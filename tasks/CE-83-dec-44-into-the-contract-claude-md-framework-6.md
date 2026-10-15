---
type: Task
id: CE-83
title: 'DEC-44 into the contract, CLAUDE.md, FRAMEWORK §6.6 and fan-out: the top-level session coordinates every request; checks and verification go to agents'
brief: 'A kit edit: ask before starting (CE-7 freeze); merge after CE-64 and CE-78, which also edit the contract'
pri: LATER
state: open
deps: []
source: session 2026-10-14g
created: 2026-10-14
moved: 2026-10-14g
updated: 2026-10-14g
---

DEC-44 (owner, 2026-10-14g): the main session is the coordinator. Told to do something, it
coordinates rather than does: "go check something" sends an agent, and verification sends out
another agent. Today the rule text says the opposite in places. A census (session 2026-10-14g,
quotes checked first-hand) found:

- **Scope:** every delegation rule is scoped to several tasks in one request. FRAMEWORK §6.6 says
  "A single-task request is unaffected." The contract § Rules, CLAUDE.md § Rules and DEC-16 say
  the same.
- **Checks:** fan-out.md § Delegating reading and auditing says a known lookup "is done inline:
  delegating it is pure overhead". The contract's Ultracode paragraph says "not a cheap lookup".
- **Verification:** the contract and §6.6 say the session "verifies first-hand before a commit, a
  push or a record write". CLAUDE.md says "Owner words and first-hand verification stay with the
  top-level session". fan-out.md says "the session merges and verifies first-hand".
- **Coordinator role:** no rule file defines it. DEC-16's 2026-10-12b amendment and US-17 ask for
  it. CE-39's roster row says "verifies first-hand".

## Scope

- Kit contract § Rules and its copy docs/framework/contract.md: widen "Several tasks in one
  session" to every request, and make verification another agent's job.
- CLAUDE.md § Rules.
- FRAMEWORK §6.6: the "Several tasks" paragraph, "A single-task request is unaffected.", the
  Ultracode "not a cheap lookup" line, and the coordinator role (CE-39's roster).
- fan-out.md and its kit copy: the inline-lookup test, "verified first-hand by the session", and
  the skeptic pass, which becomes the default verifier.
- DEC-16: amend or supersede with DEC-44. CE-39's coordinator row.

## Open points for the owner

- Owner words are still recorded verbatim by the top level, since only it holds the transcript.
- The top level still makes the final call on a verifier's verdict: it reads the report, not
  the files.
- Trivial bookkeeping (one engine op, git status) stays inline.

## Traps

- This is a kit and framework edit. CE-7's trial froze those (2026-10-14c), and DEC-43 lifts the
  freeze only for CE-77, CE-78 and CE-81. Ask before starting.
- The owner's global ~/.claude/CLAUDE.md § Delegation conflicts ("A single-fact lookup ... do it
  inline", "re-run every BROKEN repro first-hand"). The repo's CLAUDE.md wins here. Do not edit
  the global file from here (US-17).
- Several sessions edit the kit contract (CE-64, CE-78 in flight on 2026-10-14g): merge after them.
