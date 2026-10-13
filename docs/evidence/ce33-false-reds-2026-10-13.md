# False reds of the candidate G-D4 and G-D5 rules on this repo (CE-33)

FROZEN 2026-10-13c. Measured before the guards were chosen, in the CE-33 worktree at main
`2a58db2`, by a throwaway scan (kept in the gitignored scratch area; every rule it ran is written
out below, so the numbers can be re-measured without it). The rules G-D4 and G-D5 ship with were
chosen from these counts, then run as `context-engine lint` over the same tree.

**Corpus.** Every tracked `.md` that is not a record: `git ls-files '*.md'` minus `docs/stories/`,
`docs/decisions/`, `tasks/` and `docs/working/`, the kit included. 37 files on 2026-10-13c.

**Prior art.** zanzibar's `scripts/handoff_lint.py` (read 2026-10-13c): `LIVENESS_WINDOW = 10`
is a window of *lines* ("how far into a file the liveness declaration may sit"; its design said 5,
its tree needed 10), and its declaration is a bold keyword, adopted after a plain substring test
passed every frozen archive whose banner read "not a living document". Its count guard refuses a
census (`N checks`, `N tests`, `N open tasks`) with the escapes fence, quoted, dated line, banner
and a task's `## Log`, and leaves out `one` and `two` as narrative. So "within a window" in G-D4
means lines from the top, not days since an item closed.

## G-D4: which declaration form, and which window

Forms: **A** a bold keyword (`**LIVING`, the prior art's); **B** the word anywhere on the line;
**C** a frontmatter `liveness:` key, a line led by the word (after emphasis), a `Status:` list
ending in it, or `ARCHIVED <date>`. Docs declaring one, of 37, measured 2026-10-13c:

| window (lines) | A bold | B anywhere | C |
|---|---|---|---|
| 5 | 0 | 5 | 5 |
| 8 | 0 | 13 | 13 |
| 10 | 0 | 13 | 13 |
| 12 | 0 | 13 | 13 |
| 15 | 0 | 13 | 13 |

- Every declaration sits in lines 3 to 7 (a title, a blank, a status line; or a runbook
  frontmatter, whose `liveness:` is line 7; after the edits below every one is on line 3 or 7). The window is 10: the prior art's measured value,
  with room above the runbooks' line 7, and a wider one finds nothing more here.
- A finds none: the repo's declarations are plain (`LIVING. The definition ...`, `FROZEN
  2026-10-12d.`), so A would force 13 rewrites, frozen evidence docs among them. B matched only
  real declarations here (13 of 13), but it is the trap the prior art fell into, so the shipped
  form is C without the `Status:` list: a line led by the word. The one doc that needed the
  `Status:` list (`FRAMEWORK.md`, `**Framework 0.5. Status: DRAFT, LIVING.**`) was reworded to
  lead with LIVING.

The 24 docs C finds undeclared at window 10, by hand:

- **14 can carry the line, so are true reds**: `HANDOFF.md`, `README.md`,
  `src/context_engine/REGISTER.md`, the two evidence docs without a banner
  (`adhoc-baseline-2026-10-11.md`, `claude-code-hooks-2026-10-13.md`), `spike/FINDINGS.md`,
  `rituals.md` and `manual-mode.md` (each in both copies), and the kit's `HANDOFF.md`,
  `README.md`, `docs/charter.md` and `docs/criteria.md`. Each got its line; the frozen ones got a
  FROZEN banner with their bodies unchanged (P2: FROZEN carries a visible banner).
- **10 cannot, because the repo does not own their top**: the frozen provenance
  `FRAMEWORK-v0.1.md`, `v0.4` and `v0.5` (never edited); `docs/framework/contract.md` and the kit's
  `contract.md` (the framework's, byte-equal, G-D0); the kit's `bootloader.md` (the block G-D0
  compares inside `CLAUDE.md`); `CLAUDE.md` (in a fresh repo its top is that block); the session
  ledger and the kit's empty ledger (engine-written, pinned by AC-30); and `docs/charter.md`
  (owner-stamped). These are declared in `[guards] liveness_given`, a glob to a liveness, rather
  than exempted: the declaration exists, in the one place the repo owns.

The shipped rule over this repo before the docs were edited: 15 reds (the 14 above plus
`FRAMEWORK.md`), every one true, 0 false. After the edits: 0.

## G-D5: which numbers count

Scope for the variants: the 29 docs of the corpus that are not FROZEN or ACTIVE-PLAN by their own
banner, not frozen provenance and not the ledger. Prose only (fenced code and frontmatter
skipped). Number matches, measured 2026-10-13c:

| variant | rule | hits |
|---|---|---|
| N0 | every digit run | 3524 |
| N1 | N0 with backticked and quoted spans blanked and dated lines skipped (P5's forms) | 2819 |
| N2 | N1 with structural tokens stripped: `§` numbers, ids, versions, list markers, `P`/`DR` refs, links, file names, ordinals, comparisons, percentages, unit suffixes | 533 |
| N3small | a number, `one` and `two` included, directly before a wide list of 38 nouns | 237 |
| N3 | the same from three up | 27 |
| N3zan | the prior art's three patterns | 2 |
| N4 | from three up, before a census list of 21 plural nouns | 6 |
| shipped | N4 with `scenarios` added, a bound escape, on the configured `[guards] numbers` docs | 3 |

- A naive number guard (N0 to N2) is unusable: section numbers, ids, versions and rule values
  dominate, as the item predicted. Only a census pattern, a number directly before a counted
  noun, is cheap and quiet.
- `one` and `two` add 210 hits (N3small against N3), all narrative: left out, as in the prior art.
- N3's 27, by hand: 14 are `lines`, in rule values (the digest's "at most 7 lines") and format
  descriptions ("followed by four lines"); 4 are bounds ("More than 2 pauses", "at most 2
  entries", in both copies of `manual-mode.md`); 1 is a rule value ("the last 5 sessions"); 4 sit
  in evidence docs that are now FROZEN; 2 enumerate ("Three entry points", "Its four
  principles"); and 2 are real counts of the tree. Hence the
  census nouns (no `lines`, no `sessions`, plurals only: after a spelled number a singular is a
  modifier) and the bound escape: `at most`, `at least`, `more than`, `fewer than`, `less than`,
  `up to` before the number mark a rule's value. `over` and `under` are not escapes: "over 1000
  tests" is a census.
- N4's 6: 2 bounds (`at most 2 entries`, escaped, once in each `manual-mode.md`), 1 in an
  evidence doc now FROZEN (`over 10 entries`), 2 real counts (`FRAMEWORK.md`'s "The 23 components by layer";
  `criteria.md`'s "FRAMEWORK §6.6's seven steps"), 1 false red ("Its four principles, as BCA
  states them": a count of an external list, enumerated right after it). All three were edited:
  the counts dropped, the principles line reworded.
- The shipped rule over this repo: 3 reds before the edits (2 true, 1 false), 0 after.
  `CLAUDE.md` and `HANDOFF.md` hold no undated count today.

## What the counts decided

- G-D4 reads a line led by the word, a frontmatter `liveness:` key or `ARCHIVED <date>`, in the
  first 10 lines; docs the repo cannot edit are declared in `liveness_given`, not exempted.
- "History directories checked within a window" is the same line window, plus: a doc under a
  `[guards] history` directory is FROZEN, or ACTIVE-PLAN while the board item it names is open.
  No ACTIVE-PLAN doc exists in this repo today, so that rule had nothing to measure; its tests
  carry it.
- G-D5 ships on in this repo (§11.2: it measures things) and off in the kit, with the census
  nouns configurable (`count_nouns`) for repos that count other things (runs, seeds).
