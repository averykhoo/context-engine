---
type: Decision
id: DEC-210
title: "decision import lists sub-headings apart: the dry run's `## Sub-headings kept inside entries` lists every `###` to `######` heading kept inside an entry, separate from the `#`/`## ` list, which stays the short, risky one"
actor: claude-code/claude-opus-5-5
tasks: [CE-171]
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:c033b9e9653bd94591585ee2cd4c9f6069b1f35b0166e20794f58a6161d0b11e
---

The dry run of `decision import` lists, in a list of its own titled `## Sub-headings kept inside entries`, every `###` to `######` heading (as CommonMark reads one: up to three spaces of indent, then a space, a tab or the line's end) that is kept inside an entry as text, outside code fences and HTML comments, by line and entry. The `## Headings kept inside entries` list keeps only `#` and `## ` headings, and says "- none at `#` or `## `" when it is empty, so a reader who stops at it is not told the entries hold no headings. The import's summary adds a count of the sub-headings.

Why: the CE-11 intervals cutover saw "none" where 55 `###` and 10 `####` lines sat inside entries (CE-171 part 2). A `#` or `## ` heading inside an entry is the risky case (a log's own structure absorbed into the entry above); a sub-heading is usually the entry's own. Folding the two into one list would bury the risky list among benign lines and change the pinned `#`/`## ` counts; only renaming the list would leave the sub-headings invisible. `decisions.py::Parsed` carries them as `deeper`, apart from `inner`.
