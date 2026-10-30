---
type: Task
id: CE-39
title: 'Agent roster: every delegated role defined in the framework, the arbiter included'
brief: Coordinator, task owner, builder, reviewer, scout, CI watcher, install trial, hk agent, arbiter (fable)
pri: LATER
state: closed
deps: []
source: session 2026-10-13a
created: 2026-10-13
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-7]
status: deprecated
closed: 2026-10-30a
---

Owner, 2026-10-13a: the coordinator and the other agent roles should be defined in the framework, not left in a global config. Today there are no custom agent definitions (no `.claude/agents/` in this repo or `~/.claude`); every role runs on a built-in type, and the role definitions are scattered over FRAMEWORK §6.6 and the owner's global `CLAUDE.md`.

Add a roster to FRAMEWORK (§6.6 or its own section), one row per role: what it runs as, model, whether it writes, where it persists, what it returns. Roles so far:
- coordinator: the top-level session itself (DEC-16); records owner words, verifies first-hand, reports progress
- task owner: one per task, pushes work down to a workflow or its own agents
- builder and fixer; adversarial reviewer (read-only, probes allowed)
- scout or auditor: `Explore` when acted on the same turn (cannot persist), otherwise a writing agent
- CI watcher; fresh-user install trial; `.scratch/` sweep auditor
- hk agent (CE-12), limited to `hk_` tools
- **arbiter (owner, 2026-10-13a):** makes decisions against the repo's goals and thinks open questions through in detail; runs on `fable`. One of the owner's two standing `fable` cases, the other being the difficult parts of proofs (recorded as an amendment to DEC-18).

Decide whether the kit ships the subagent roles as `.claude/agents/*.md` (prompt, tools and model built in, picked by name) or as roster text only. The coordinator is the main conversation, so its definition is the contract rule plus its roster row.

## Log

- 2026-10-13a (claude-code/claude-opus-5-5): docs checked: docs/evidence/claude-code-hooks-2026-10-13.md. .claude/agents/*.md takes model: fable among others, so the arbiter can be a named agent; project agents win over user agents. The main thread can run as a named agent (--agent or "agent" in settings.json), but its prompt then replaces Claude Code's default system prompt: weigh that before making the coordinator one.
- 2026-10-13a (claude-code/claude-opus-5-5): Owner, DEC-18 amended 2026-10-13a: two standing fable cases, the arbiter (decisions against the repo's goals, open questions thought through) and the difficult parts of proofs.
- 2026-10-20b (claude-code/claude-opus-5-5): Coordinator row superseded by CE-83 (17470c8): the top-level session itself (DEC-16, DEC-44, DEC-60; FRAMEWORK §6.6 'The coordinator'); every request, and the board by default; every task to an ultracode subagent, checks and verification to agents; keeps owner words verbatim, the final call on a verifier's report (not the files), and trivial bookkeeping (DEC-63); reports progress. Its 'verifies first-hand' wording no longer holds.
- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in cdc7261 and 9bcdfc3 (lane 7f298c7, 1eb1ba2), cite in 90ce0b9: FRAMEWORK §6.6 now has 'The roster', one row per delegated role (coordinator, task owner, builder/fixer, verifier, adversarial reviewer, scout/auditor, ranking agent, watcher, install trial, .scratch/ sweep auditor, housekeeping agent, arbiter), each giving what it runs as, its model tier, what it writes and what it returns. The arbiter runs on fable where the owner asked, as one agent; the housekeeping agent works only through hk_ operations, op-logged in place of a persist file; the watcher writes nothing and never pushes. The kit ships the roster as text, not named agents (DEC-97). fan-out.md points at it. Pinned by AC-113 and tests/test_roster.py.
