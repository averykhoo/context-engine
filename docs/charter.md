---
type: Charter
title: context-engine charter
description: What the engine is for, how success is measured, what is out of scope, and which principle wins a tradeoff
actor: agent (claude-opus-5-5, reconstructed from the owner's words of 2026-10-07 and 2026-10-08)
charter_status: unconfirmed   # owner review pending: ASK-1
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
---

# Charter (UNCONFIRMED: reconstructed by an agent, awaiting the owner's review, ASK-1)

Reconstructed from the owner's own words, which are recorded verbatim as stories in
`docs/stories/` (US-1 to US-8) and in `docs/framework/FRAMEWORK.md` §12. Per the framework
(§11.4), a reconstructed charter is `unconfirmed` until the owner reviews it; until then it
guides work but does not settle a tradeoff the owner has not spoken to.

## What this is

The record engine specified in `docs/framework/FRAMEWORK.md` §8.0: one Python package that owns
every component of an agent-built repo that is a set of id'd records (tasks, owner questions,
batons, pause blocks, ledger entries, decisions, stories, deviations), stores them as OKF
markdown files, and exposes them through a CLI, a per-session MCP server, and a no-model
housekeeping script. It is pointed at a repo; it is never installed into one.

## Goals, each with how it is measured

| # | Goal | Measured by | Stories |
|---|---|---|---|
| G1 | **Sessions stop spending context on reading and re-reading files to edit records** | context read at session start and clean close, against a baseline taken by hand before cutover (the adhoc trial rubric, CE-4 / CE-7) | US-1, US-6 |
| G2 | **Every place has room for its records and checks on what is inside** | each record kind has a schema, a cap and a way out; each rule has a write-time refusal and a rest-time lint that has been shown to fail (sabotage) | US-2 |
| G3 | **Routine upkeep is done by tools, not by hand** | housekeeping operations replace hand edits for stamps, comments, expiry and evidence-backed closes; no `hk_` operation can make a judgement call | US-3, US-8 |
| G4 | **Nothing to run by hand: the engine starts and stops with each session, per repo** | `.mcp.json` in a target repo is the whole setup | US-4 |
| G5 | **Records stay plain files that humans and git can read and edit** | records are OKF markdown; a hand edit is legal and is caught by lint if it breaks something; no database is a source of truth | US-5, US-7 |
| G6 | **Works for every repo the owner has**, whatever its language or environment | adopted by adhoc (first), then intervals, then zanzibar and audio-workspace | — |

## Non-goals (owner's words)

- **A server the owner has to start or manage** (US-4).
- **SQLite or any database as the source of truth**: *"not as friendly to human readers/editors
  or git"* (US-5; DEC-9). A derived, disposable index is allowed.
- **Edit subagents, for now**: *"if a script (or mcp) might work lets try that out first"*
  (DEC-4).
- **Migrating existing repos' records yet**: *"for now we'll work on the framework not the
  migration"* (DEC-5). The adhoc trial is the first adoption, on a branch.

## Ranked principles (for tradeoffs)

Agent proposal, for the owner to confirm or reorder (ASK-1):

1. **Never lose owner words or evidence** (FRAMEWORK P9, P10).
2. **Files stay human-readable and git-friendly** over speed or cleverness (G5).
3. **A mechanical refusal beats a written warning** (FRAMEWORK §0.2).
4. **Less context per ritual** over more features (G1).
5. **One versioned implementation**: never copy engine code into a target repo (DEC-1, DEC-2).

## Owner mandates

None beyond the owner's global `CLAUDE.md` (commit freely when green; push and open PRs only
with permission; every push gets a CI watcher; Recycle Bin for bulk deletes; never bare
`python`).
