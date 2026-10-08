# context-engine: contract

framework: 0.5-draft (manual mode, DEC-7)

This repo builds the record engine specified in `docs/framework/FRAMEWORK.md` (§8.0), and runs
that framework on itself **by hand** until the engine can do it (DEC-7). What is true now and
what is next live in `HANDOFF.md`; this file holds only what is durable.

## Where things live (routing table; moves to `context.toml` in CE-8)

| Component (FRAMEWORK §2) | Here | Change mode |
|---|---|---|
| Spec | `docs/framework/FRAMEWORK.md`; a change gets a row in its §13 | replaced |
| Frozen provenance | `docs/framework/FRAMEWORK-v0.*.md`, `A-*.md` to `D-*.md`, `review/` | never edited |
| Charter | `docs/charter.md` (confirmed 2026-10-08, DEC-10) | replaced, owner-stamped |
| Stories (owner's words) | `docs/stories/US-n-<slug>.md` | append-only: amend, never rewrite |
| Criteria | `docs/criteria.md` (`AC-n`), claimed by `@pytest.mark.criterion("AC-n")` | replaced, ids kept |
| Decisions | `docs/decisions/DEC-n-<slug>.md`, one record each (FRAMEWORK §6.5) | append-only: `## Amendments` |
| Tasks and owner questions | `tasks/CE-n-<slug>.md`, `tasks/ASK-n-<slug>.md` (board size 2) | frontmatter by rule, bodies by hand |
| Orientation note | `HANDOFF.md` | replaced at clean close |
| Session ledger | `docs/ledger/session-log.md` | append-only, one entry per session |
| Evidence | `docs/evidence/<topic>-<date>.md` | ACTIVE-PLAN, then FROZEN |
| Spike evidence | `spike/` (`FINDINGS.md` is the result; the probes show how) | frozen per run |
| Scratch | `.scratch/` (gitignored crash bag) | throwaway |

**Id prefixes** (zero collisions on 2026-10-08, DEC-7): tasks `CE-n`, decisions `DEC-n`,
stories `US-n`, criteria `AC-n`, owner questions `ASK-n`. Never reuse or renumber an id.
OKF reserves `status`: use `state`, `decision_status`, `story_status`, `charter_status`.

## Environment

- Interpreter: `C:/Users/user/anaconda3/envs/context-engine/python.exe` (Python 3.12).
  Bare `python` is broken on this machine; always use the full path.
- Install for development: `<interpreter> -m pip install -e ".[dev]"`.
- **The engine runs from its own env and is pointed at a repo; it is never installed into a
  target repo's environment** (DEC-1).

## Gate

`<interpreter> -m pytest -q` from the repo root. Run it before every commit that touches
`src/` or `tests/`, and before every push. Every new record file must parse: a YAML scalar with
a colon needs quotes (it broke DEC-6 once).

## Sabotage rule (owner mandate, DEC-11)

**No test or guard is believed until it has been seen to fail.** For every new test, guard or
refusal: break what it protects (edit the code, corrupt the fixture, drop the check), run it and
watch it go red for the right reason, then restore. Record it in the commit message as
`Sabotage: <what was broken> -> <test> red`. A criterion moves to `tested` only after its
claiming test was sabotaged. When G-T5 (mutation per criterion, CE-14) exists, it does this
mechanically and this hand step becomes its fallback.

## Rituals (manual mode: FRAMEWORK §6, done by hand)

**Session start:** follow `HANDOFF.md § Next session: start here`. Open batons and pause blocks
first; raise every NEXT-tier `ASK-n` in chat, one line each.

**Owner gives intent** (§6.2): record it **verbatim, now**. Behaviour-shaped → a new story or an
amendment; choice-shaped → a `DEC-n` with `actor: owner`, or a charter edit. Tell the owner in
one line which it became. An answer to an `ASK-n` becomes a decision, then the question's
`state: closed` with `closed:` set.

**Clean close** (§6.3), in this order:
0. Every owner word from this session is recorded.
1. Run the gate.
2. Write the ledger entry: mint the key as `max(newest ledger key, banner key) + 1 letter`;
   `rows:`, receipts (gate result, `read:`, `asked:`), `summary:` (the digest, at most 7 lines),
   `Still owed:`.
3. Replace the HANDOFF banner (re-read HANDOFF first: another session may have written it).
4. Update task files: `state`, `pri`, `moved`/`updated` with the session key, a dated `## Log`
   line; keep NOW at exactly 1 and NEXT at most 5; mirror the board table in HANDOFF.
5. Durable rules come here; method lessons go into a runbook.
6. Anything skipped becomes a baton in HANDOFF.
7. Gate again, then commit by path. Push only with the owner's permission; every push gets a
   CI watcher (global `CLAUDE.md`).
8. The digest in chat.

**Pause** (§6.4): owner words recorded, evidence out of `.scratch/`, a three-line ledger entry
(`kind: pause`), a pause block in HANDOFF; commit those by path.

## Rules

- Commit by path (`git commit -o <paths>`); never `git add -A`, never `git stash`.
- Re-run `git status` and `git log -3` right before editing HANDOFF or the ledger and before
  committing: sessions here may run concurrently.
- Frozen provenance is never edited (see the routing table).
- `spike/` holds probes whose findings are transcribed into the spec; the probes are kept as
  evidence of how a finding was reached.
- Cite code as `file::symbol`, never by line number; grep that a symbol exists before citing it.
