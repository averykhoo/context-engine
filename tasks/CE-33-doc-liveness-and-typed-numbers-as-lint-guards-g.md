---
type: Task
id: CE-33
title: Doc liveness and typed numbers as lint guards (G-D4, G-D5)
brief: Measure false reds on this repo before choosing the exemptions; frozen provenance is never edited
pri: NEXT
state: open
deps: [CE-14]
source: session 2026-10-12d
created: 2026-10-12
moved: 2026-10-13a
updated: 2026-10-13c
---

Split from CE-14 (2026-10-12d), which built the rest of the §8.3 doc guards in `src/context_engine/guards.py` with `[guards]` path lists in context.toml. Both are §11.2-triggered here: the repo keeps evidence docs ("the repo measures things").

- **G-D4:** every doc declares its liveness (LIVING, ACTIVE-PLAN, FROZEN) near the top; history directories are checked for frozen banners within a window. On 2026-10-12d only 5 of 26 tracked non-record docs declared one (counted by grep of the first 12 lines), and `docs/framework/FRAMEWORK-v*.md` (frozen provenance) cannot be edited to add one, so it needs a declared exemption or a route-level liveness. The kit's docs need the line too. Decide what "within a window" means (days since the item closed?).
- **G-D5:** derivable counts only in generated blocks; a typed number takes one of P5's four forms. A naive scan flags section numbers, ids, versions, list markers and rule values ("NEXT <= 5"); measure the false reds first.

## Traps

- A guard that fails by passing: sabotage each one (tools/sabotage_ce14.py is the pattern).
- Kit files must not carry this repo's ids (tests/test_kit.py leak check).

## Read first

- `docs/framework/FRAMEWORK.md` P2 (liveness), P5, §8.3 G-D4 and G-D5
- `src/context_engine/guards.py` (the shared prose reader and the `[guards]` lists)

## Log

## Design review

affects: every session in a repo whose context.toml lists docs for G-D4 or G-D5 (this repo; G-D4 in every fresh kit init); an adopting repo whose existing docs G-D4 now reads; the owner and plain-git humans who write docs by hand; the session that freezes, archives or copies a doc
- eliminated: a fresh kit init or an upgraded repo goes red on the new guards | rung: eliminate | control: the new [guards] keys default to off; the kit docs carry their line and the template's liveness_given covers what they cannot; tests/test_kit.py::test_an_empty_repo_bootstraps_with_init_alone_and_runs_a_whole_session lints clean
- reduced: a liveness word in passing (mid-line, on a wrapped line, in fenced code, inside a longer word) passes a doc as declared | rung: reduce | control: guards.py::declared reads only a block-opening line led by the whole word; tools/sabotage_ce33.py
- reduced: a guard reads nothing and stays silent | rung: reduce | control: G-D4 is red on a liveness list holding no doc, G-D5 on a numbers list of only FROZEN or ACTIVE-PLAN docs, and both on a missing listed path
- reduced: frozen provenance must be edited to pass | rung: reduce | control: [guards] liveness_given declares it by glob; a glob matching no file is red
- reduced: an ACTIVE-PLAN doc outlives its item | rung: reduce | control: G-D4 is red on an ACTIVE-PLAN doc whose window names no board item, or only closed ones
- reduced: a count of the tree typed in a LIVING doc goes stale unseen | rung: reduce | control: G-D5 over [guards] numbers, with P5's forms
- residual: G-D5 misses counts outside its census form (another adjective, as in "four method runbooks"; `**23**`; spelled numbers above twenty; singulars; a count split across lines) | rung: individual | why: the measurement showed wider patterns are noise (27 hits, 25 not counts) | control: the numbers docstring's Not checked list; review
- residual: G-D5 is red on a label or a rule value without a bound word (`Step 3 checks`, `the last 5 entries`) | rung: individual | why: telling a label from a count needs judgement, and a wider bound escape is a false-pass hole | control: the remedy names backticks
- residual: a YYYY-MM-DD anywhere on a line (a link target too) exempts every count on it | rung: individual | why: P5's form is a key on the line, and a narrower rule cannot be followed by hand | control: review
- residual: G-D5 trusts a FROZEN or ACTIVE-PLAN word G-D4 does not check when a numbers doc is not under liveness | rung: individual | why: both lists are config | control: §8.3 says to list each numbers doc under liveness too, and this repo does
- residual: a liveness_given glob wide enough to cover every listed doc passes them all | rung: individual | why: reviewed config; only a stale glob is checked | control: review of context.toml changes
- residual: a declaration may be false (a LIVING doc gone stale) | rung: individual | why: no mechanical check (DR9) | control: housekeeping and review
- residual: an adopting repo is red after init until its own docs declare liveness | rung: individual | why: P2 asks every doc to declare, so hiding them would be a false green | control: kit README §3, the remedy text
- residual: banner set and other writes can store text G-D5 reds, and the engine commits it | rung: individual | why: no write-time check for G-D5 (G-D8 has the same gap) | control: lint in the gate before the next commit
- residual: the shared prose() reads a leading `---` break as frontmatter and lets `~~~` close a ``` fence, hiding lines from G-D5 (and G-D3, G-D7) | rung: individual | why: pre-existing in the shared reader | control: none yet; a follow-up
F: goes stale when FRAMEWORK P2 or P5 change, when the repo adopts a banner style declared() does not read, or when count_nouns stops naming what the repo measures; tools/sabotage_ce33.py (60 rows) and the near-miss fixtures in tests/test_guards.py catch a drift in the code
A: switched off by emptying [guards] liveness, history or numbers, or with [guards] off; manual-mode § lint has each guard's by-hand steps; the measurement is docs/evidence/ce33-false-reds-2026-10-13.md
M: one reader (guards.py::declared, liveness_of) serves both guards; config is validated at load (config.py::from_dict); the kit's count_nouns is pinned to config.py::COUNT_NOUNS by a test
E: reuses guards.py::docs and prose, the [guards] path-list pattern, and the zanzibar prior art (LIVENESS_WINDOW, check_restated_counts); reviewed by false-pass, false-red/deploy and spec-fidelity lenses plus a skeptic: 13 FIX (fixed), 21 DOC (written), 3 follow-ups, 3 rejected
