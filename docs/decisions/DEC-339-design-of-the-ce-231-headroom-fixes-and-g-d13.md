---
type: Decision
id: DEC-339
title: Design of the CE-231 headroom fixes and G-D13, the guard that keeps record ids out of reader-facing docs
actor: claude-code/claude-opus-5-5
decided: 2026-11-12
session: 2026-11-12b
decision_status: ACCEPTED
body_sha: sha256:623a9c5fce0d56bb7193c246c1463133d5f78067501f460e7563ef07f4320fcb
---

The planner's design calls for the CE-231 headroom follow-ups and CE-233 (the reader-doc guard DEC-338 asks for). An agent's calls, cheap to undo: PROVISIONAL until the owner reviews them.

**CE-231 follow-ups**

1. **One remedy.** A new `cap_remedy(component)` in guards.py returns G-D1's line/byte remedy (where cut text goes, and "delete it here only once it has landed there"); `cap_failures` and `cap_warnings` both call it, so the warning cannot drift from the failure. Rejected: a module constant with a `{component}` placeholder (a format call at each site is a second place to get wrong); a shorter warning remedy (the review's finding: it dropped the AC-105 point).
2. **Headroom is off with G-D1.** `headroom(e)` returns nothing when `[guards] off` names G-D1, the same `"<id>" in config.guards.off` test the write-time checks use. `cap_warnings` stays a pure per-text function, as `cap_failures` is, and its caller decides. Rejected: making warnings `Failure` objects so `Engine.lint`'s filter drops them (a warning typed as a failure is one refactor away from failing lint, the thing the warning must never do).
3. **The percentage is floored.** `_headroom_pct` works in integer tenths (`value * 1000 // cap`), trailing `.0` dropped: 9996 of 10000 reads 99.9, 19 of 20 reads 95, exactly at the cap reads 100, over it its floored figure (21 of 20 reads 105; 10001 of 10000 reads 100, and the G-D1 failure on the same file says it is over). Rejected: printing 99.9 as a ceiling (still hides how close the file is) and float rounding (`round` and `:.1f` round half up and 9996 of 10000 shows 100).

**CE-233: G-D13**

4. **A new id, G-D13**, the next free doc-guard id (§8.3 runs G-D0 to G-D12; no G-D13 exists). Rejected: folding it into G-D3 (G-D3 checks that a citation resolves; this one forbids citing at all, and a repo may want one on and the other off).
5. **Config:** `[guards] reader_docs`, a list of files and directories like `links` and `numbers`; empty is off; a listed path that does not exist is red, as for G-D3 and G-D5. Not `readers` (the gate already has `--readers` for tests that read files). This repo lists `README.md`; the kit template carries `reader_docs = []` (the template must name every `[guards]` key), so an adopted repo whose README cites ids stays green until it opts in.
6. **Which ids:** every series the repo keeps: each kind's prefix, the prefixes leading the criteria rows (`[working] criteria`), the register's entry prefixes (`[working] register`), and `GOAL-n` and `G-n` while `[guards] charter` is set; standing alone (not glued to a letter, digit or `-` on either side), case-sensitive. A guard id (`G-D1`: a letter after the dash), a section (`§8.0`), a session key and an id of a series the repo does not keep are not ids. Rejected: any `[A-Z]+-[0-9]+` (reads UTF-8 and SHA-256 as ids); kinds' prefixes only (lets criteria, register and goal ids through, though they are records a stranger cannot open).
7. **What is read:** prose outside fenced code and frontmatter, inline code included. Not read: link destinations, reference-definition lines and URLs, since a reader does not see them, and a link to a records-site page is the orientation the remedy asks for. Rejected: exempting inline code, as G-D3's record citations do (a backticked id is as opaque to a stranger as a bare one, and backticks would become the way round the rule); exempting fenced code is kept, as every doc guard does, since a code block shows commands and output.
8. **Reporting:** one failure per distinct id per line, `line <n>: cites the record id <id>`, with one remedy: give the reader the words, or point at the board (`context-engine task list`) or the records site (`context-engine site build`). Not checked: progress prose that cites no id (a judgement, left to review), and a write-time twin (the engine writes no reader-facing doc).
