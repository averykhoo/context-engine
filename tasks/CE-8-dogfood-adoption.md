---
type: Task
id: CE-8
title: "The engine adopts this repo's hand-written records"
brief: "Stamp body_sha, make lint green, then switch this repo's rituals from hand edits to the tools"
pri: NOW
state: closed
deps: [CE-2]
source: session 2026-10-08a
created: 2026-10-08
moved: 2026-10-08f
updated: 2026-10-08f
closed: 2026-10-08f
status: deprecated
---

This repo runs the framework by hand (DEC-7). Once the engine can read and lint its records,
point it here: stamp `body_sha` on stories and decisions, fix what lint finds, move the
routing table from `CLAUDE.md` into `context.toml`, and rewrite the rituals in `CLAUDE.md` to
use the engine's operations.

US-11: the hand procedure is kept, not replaced. Before the rewrite, write a manual-mode runbook
(FRAMEWORK §7.5) giving the by-hand equivalent of every `ce` operation, for repos with no
Python. Add a guard that every `ce` subcommand has a runbook section (sabotage it: delete a
section, watch the gate go red).

## Traps

- Stamping freezes a body (G-D10): stamp only stories and decisions whose text is final; a later change is an `amend`.
- `status` and the other board-owned keys change only through their operation; `ce task set` refuses them (DEC-14 item 7).
- `session close` needs `--guards` and `--read`, and `--asked` naming every NOW or NEXT question; set `CE_SESSION` and `CE_ACTOR` once per session.
- The banner is written only with the hash `ce banner show` printed; another session's write in between makes `banner set` refuse.

## Read first

- `ce --help` and `src/context_engine/cli.py::build`
- `context.toml` § [working]; DEC-14
- `CLAUDE.md` § Rituals, the text this task rewrites

## Log

- 2026-10-08c: deps CE-3 -> CE-2. Adopt with the CLI as soon as it exists; the MCP server (CE-3)
  then lands on records that already run through the engine.
- 2026-10-08: scope widened by US-11: a manual-mode runbook covering every `ce` operation, with
  a parity guard, comes before the `CLAUDE.md` ritual rewrite.
- 2026-10-08e (claude-code/claude-opus-5-5): manual-mode runbook written (docs/runbooks/manual-mode.md, US-11): every ce operation by hand, each with its Why; parity guard tests/test_runbook.py (AC-21). Verifying it against the code found okf._section_span prefix-matching headings (## Logs, ## Read first); fixed. Remaining: stamp, lint green, context.toml routing, CLAUDE.md rituals as ce commands with the runbook as fallback; add ce stamp/amend to the CLI (the runbook covers them by hand).
- 2026-10-08f (claude-code/claude-opus-5-5): ce record new/stamp/amend and ce routes added; 24 records stamped; lint clean and in the gate (AC-23); routing in context.toml [[routes]] with G-R1; CLAUDE.md rituals rewritten as ce commands with the runbook as fallback; DEC-7 amended. AC-22 to AC-25 tested (tools/sabotage_ce8.py, 11 rows red).
- 2026-10-08f (claude-code/claude-opus-5-5): closed: done: this repo runs through the engine
