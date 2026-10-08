---
type: Charter
title: context-engine charter
description: What the system is for, how success is measured, what is out of scope or forbidden, and which principle wins a tradeoff
actor: agent (claude-opus-5-5, reconstructed from the owner's words of 2026-10-07 and 2026-10-08); confirmed and widened by the owner 2026-10-08 (DEC-10)
charter_status: confirmed
confirmed: { by: owner, on: 2026-10-08, session: 2026-10-08b, decision: DEC-10 }
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T17:00:00+08:00 }
---

# Charter

Reconstructed by an agent from the owner's own words (stories US-1 to US-9 in `docs/stories/`
and `docs/framework/FRAMEWORK.md` §12), then confirmed by the owner, who widened the scope and
turned one non-goal into an anti-goal (ASK-1, answered as DEC-10; words verbatim in US-9).

## What this is

**The whole system described in `docs/framework/FRAMEWORK.md`, built as something the owner
can deploy across all their repos** (US-9): the components (charter, stories, criteria,
contract, orientation note, board, batons and pauses, decisions, ledger, deviations, evidence,
archive), the rituals that run them, the guard catalogue that checks them (§8.1 to §8.5), and
the bootstrap and adoption path for new and existing repos (§6.9, §10, §11).

**The record engine (§8.0) is the first piece and the backbone:** one Python package that owns
every component that is a set of id'd records, stores them as OKF markdown, and exposes them
through a CLI, a per-session MCP server, and a no-model housekeeping script. It is pointed at a
repo; it is never installed into one.

**Order (DEC-10):** build it here and dogfood it on this repo first; work out how other repos
adopt it after that.

## Goals, each with how it is measured

| # | Goal | Measured by | Stories |
|---|---|---|---|
| G1 | **Sessions stop spending context on reading and re-reading files to edit records** | context read at session start and clean close, against a baseline taken by hand before cutover (CE-4 / CE-7) | US-1, US-6 |
| G2 | **Every place has room for its records and checks on what is inside** | each record kind has a schema, a cap and a way out; each rule has a write-time refusal and a rest-time lint that has been shown to fail (sabotage) | US-2 |
| G3 | **Routine upkeep is done by tools, not by hand** | housekeeping operations replace hand edits for stamps, comments, expiry and evidence-backed closes; no `hk_` operation can make a judgement call | US-3, US-8 |
| G4 | **Nothing to run by hand: it is text in a repo that Claude Code manages** | committed files (`.mcp.json`, `context.toml`, `CLAUDE.md`) are the whole setup; any server is started and stopped by Claude Code as part of a session ritual | US-4, US-9 |
| G5 | **Records stay plain files that humans and git can read and edit** | records are OKF markdown; a hand edit is legal and is caught by lint if it breaks something; no database is a source of truth | US-5, US-7 |
| G6 | **Works for every repo the owner has**, whatever its language or environment | dogfooded here first (CE-8), then adopted by the owner's other repos (adhoc, intervals, zanzibar, audio-workspace) | US-9 |
| G7 | **The whole framework is built, not just the engine** | every component, ritual and guard in FRAMEWORK.md is either built (tool, guard or skill), or written down as deliberately prose-only, or explicitly deferred with a reason | US-9 |

## Anti-goals (must not happen)

- **A server the owner has to start or manage** (owner: *"not just a non-goal, its an
  anti-goal"*, US-9). Claude Code may start its own server as a ritual; the owner never does.

## Non-goals (owner's words)

- **SQLite or any database as the source of truth**: *"not as friendly to human readers/editors
  or git"* (US-5; DEC-9). A derived, disposable index is allowed.
- **Edit subagents, for now**: *"if a script (or mcp) might work lets try that out first"*
  (DEC-4).
- **Migrating existing repos' records yet**: *"for now we'll work on the framework not the
  migration"* (DEC-5), and *"lets start with it in here and dogfood it, then we'll figure out how
  to adopt it in new repos"* (US-9).

## Ranked principles (for tradeoffs)

Proposed by the agent; the owner found it *"not incorrect"* (DEC-10):

1. **Never lose owner words or evidence** (FRAMEWORK P9, P10).
2. **Files stay human-readable and git-friendly** over speed or cleverness (G5).
3. **A mechanical refusal beats a written warning** (FRAMEWORK §0.2).
4. **Less context per ritual** over more features (G1).
5. **One versioned implementation**, built and dogfooded here; never copy engine code into a
   target repo (DEC-1, DEC-2, DEC-10).

## Owner mandates

None beyond the owner's global `CLAUDE.md` (commit freely when green; push and open PRs only
with permission; every push gets a CI watcher; Recycle Bin for bulk deletes; never bare
`python`).
