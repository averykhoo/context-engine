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
updated: 2026-10-19a
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

## Log

- 2026-10-15a (claude-code/claude-opus-5-5): DEC-45 widens scope: CI watcher brief (procedures § Push and CI, fan-out § Watchers, both kit copies) names the watcher's model (haiku or sonnet, not just 'a cheap model'), and adds a step for when the excerpt is not enough: the watcher saves the full failed-job log (gh run view <id> --log-failed) beside its report, or the coordinator sends a second watch-only agent for it
- 2026-10-15a (claude-code/claude-opus-5-5): Model census (2026-10-15a, .scratch/wf-2026-10-15a/model-census.md, quotes checked first-hand): FRAMEWORK §6.6 already says 'The default for delegated work is the cheaper model that can do it.' (kit carries it) but CLAUDE.md § Rules names no default or cheaper model, so fan-out.md's pointer ('The repo's values (its default and cheaper models, for one) are in its CLAUDE.md') dangles, and a reader of CLAUDE.md falls through to the owner's global default of opus. Add to CLAUDE.md § Rules: the cheapest viable model per subagent (haiku for watchers, sonnet for bulk reading and census, opus for code and review). A per-role roster stays CE-39's.
- 2026-10-19a (claude-code/claude-opus-5-5): DEC-60 (owner, 2026-10-19a) widens scope: the coordinator runs every task through ultracode subagents, even a single task, never doing it itself; working the board defaults the session to the coordinator role; every subagent persists to a file as it goes (already in fan-out.md § Delegating reading and auditing; make the contract say it too, since the Windows crash of 2026-10-17/18 killed a session). This also settles the census's 'A single-task request is unaffected.' line: it goes.
