---
type: Task
id: CE-98
title: 'decision import loses text silently: inner ## headings, amendment headings, letter ids, date-as-actor'
brief: 'The import never drops text silently: unplaceable text is a refusal naming its line'
pri: LATER
state: closed
deps: []
source: session 2026-10-17b
created: 2026-10-17
moved: 2026-10-19e
updated: 2026-10-19e
status: deprecated
closed: 2026-10-19e
---

Found while assessing audio-workspace for a full migration (CE-43, DEC-51). Verified by an agent on 2026-10-17b (synthetic fixtures through `decisions.py::parse_entries` in process and `decision import --dry-run` in a throwaway repo, which exited 0 with no warning), and A re-run first-hand by the session the same day.

Defects in `src/context_engine/decisions.py`:

- **A, silent text loss.** `STOP_RE` in `decisions.py` (`^#{1,2} `; the fix removes it) ends an entry at any `## ` heading, so text between an inner `## ` and the next `### ` entry belongs to no entry and is dropped with no refusal. audio-workspace `docs/decisions.md` (29,402 lines, measured 2026-10-17): 73 entries hold an inner `## `; 5,344 lines would be lost (4,428 non-blank).
- **B, amendment headings fold into the wrong entry.** `decisions.py::ENTRY_RE` needs a dash right after the id, so `### D-107 FIX`, `### D-75 AMENDED`, `### D-4 (amended)` are not entries; their text folds into the entry above. Same file: 10 such headings, 6 fold into a different decision (D-107 FIX into D-109, D-4 (amended) into D-12).
- **C, letter-suffixed ids** (`D-159b`): `ENTRY_RE`'s id group is `-\d+`, so the entry folds into the one above, or is dropped with no refusal when it is the first heading.
- **D, a bare date becomes the actor.** `parse_entries` takes `attr.split(",")[0]` as actor and refuses only an empty one, so `*(2026-07-25)*` gives `actor='2026-07-25'`. Same file: 15 headings.
- **E, not a bug, the scale:** 126 of the 303 entry headings (D-12..D-153) have no `*(actor, date)*`, so the import refuses (as designed); the migration needs a normalisation step or an import option for unattributed entries.
- **Minor:** `decision import --dry-run` left an empty `.context/` directory in the target (probably the lock), so the dry run is not write-free.

Coverage (`tests/test_decisions.py`): `test_import_keeps_every_id_and_text_verbatim_stamped_with_links_both_ways` only checks a `## ` after the LAST entry is excluded; nothing covers A between entries, B, C or D. `test_import_is_all_or_nothing` covers E's refusal.

Fix direction: the import must never lose text silently. Any text it cannot place is a refusal naming the line, or kept in the entry; amendment headings and letter ids get an explicit rule (refuse with a remedy, or attach to their own id); a date-shaped actor is refused. Each fix gets a sabotaged test (DEC-11).

## Log

- 2026-10-19e (claude-code/claude-opus-5-5): closed: a8879f9: the import keeps every line inside an entry or names it, and refuses every heading it cannot read; the dry run writes nothing. Gate green 2026-10-19 (898 passed). The leftover #/####-level entry-shaped heading is CE-100.
