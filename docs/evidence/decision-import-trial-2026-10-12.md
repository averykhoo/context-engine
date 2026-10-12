# Decision import trial on a copy of adhoc's log, 2026-10-12 (CE-5, US-7)

FROZEN 2026-10-12d. The import itself, into adhoc, is CE-7; this run only proves the importer on
a copy, as CE-5's acceptance asks ("Test the importer on a copy").

**Question:** does `context-engine decision import` turn adhoc-microphone-array's single-file
`docs/decisions.md` into decision records that keep every id and every word, with nothing lost
and nothing written twice?

**Method.** A throwaway git repo (`mktemp -d`), `context-engine init --prefix decision=D` (so the
series keeps adhoc's `D-n`, FRAMEWORK §11.4), then a copy of adhoc's
`docs/decisions.md` (72,345 B; sha256 `9d140f6c...e40caf`; last changed in adhoc commit
`84d3d05`, 2026-10-12 11:26 +0800). Then `decision import --dry-run`, `decision import`,
`lint`, and the independent check `tools/check_decision_import.py <repo> <copy>`, which does not
use the importer's parser: it checks each record's text is a verbatim slice of the source, and
each non-blank, non-heading source line from `## Entries` on, and each table row, appears in
some record. The temp repo was deleted afterwards.

## Result (engine at the CE-5 commit, 2026-10-12d)

```
dry run, nothing written: would import 40 entries (D-1..D-40, ids kept); 18 rejected rows as D-41..D-58; 4 heading notes kept as amendments into docs/decisions
imported 40 entries (D-1..D-40, ids kept); 18 rejected rows as D-41..D-58; 4 heading notes kept as amendments into docs/decisions, each stamped; index docs/decisions/index.md regenerated
lint: clean
records: 58
records whose text is not a verbatim slice of the source: none
entry lines checked: 936, not in any record: 0
table rows checked: 18, not in any record: 0
headings checked: 40, id/title/note not kept: none
  D-27: SUPERSEDED {'superseded_by': ['D-29']}
  D-29: BUILT {'supersedes': ['D-27']}
  D-12: BUILT {'narrowed_by': ['D-30']}
  D-30: BUILT {'relaxes': ['D-12']}
  D-2: BUILT {'narrowed_by': ['D-26']}
  D-26: BUILT {'relaxes': ['D-2']}
```

`why D-12` answered D-30 via `relaxes`; `decision find --status REJECTED` listed D-41 onwards;
the index held 58 lines under `## BUILT`, `## SUPERSEDED` and `## REJECTED`. Actors: 18
`owner`, 11 `agent` plus the 18 rejected rows (`agent`), 9 `owner asked + agent`, 2
`owner + agent`. Five entries keep their whole heading parenthetical in `attribution:` because it
says more than actor and date (D-1, D-2, D-3 `brief added`; D-11 `amended by evidence`; D-29
`on the agent's recommendation`).

## What CE-7 should look at before cutover

- **D-27 is marked wholly SUPERSEDED,** but its note says "SUPERSEDED by D-29 (FireRedVAD) for
  the gate backend; the permissive rule stands". The note is kept verbatim as an amendment; a
  partial supersession has no status of its own. CE-7 decides whether D-27 stays SUPERSEDED or
  gets an amendment saying which part stands.
- **Every imported record's `session` is the importing session,** not the session that decided
  it (the log has no session keys); `imported_from:` marks them. This is the residual the CE-5
  design review sends to the register.
- **The 18 REJECTED rows have no `reopen_if:`.** The table has no such column; the reasoning is
  under the entry each row's `refs` names.
- **Status defaults to BUILT** for every entry not superseded by a heading note; the log does not
  say which entries are PROVISIONAL or DEFERRED.
