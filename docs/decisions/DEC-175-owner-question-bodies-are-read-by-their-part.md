---
type: Decision
id: DEC-175
title: Owner-question bodies are read by their part names and list nesting, and task section adds a section above the Log
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-158]
decided: 2026-11-07
session: 2026-11-07d
body_sha: sha256:7a2dd3c033fbde65fa116aa63a7cb4db6f72a7624ca2758f1c24cd30447d0e08
---

An agent's call under P8 (cheap to undo), made by CE-158's builder in session 2026-11-07d. Not owner words.

**Call.** How an owner question's body is read (guards.py::ask_parts, guards.py::ask_options), and where `task section` puts a missing section (okf.py::set_section):

- A missing section goes in above `## Log`, not at the end, so the Log stays a board item's last section and G-W4's remedy (`task section <id> <part> "<text>"`) clears what it names. With no Log, or for the Log itself, it still goes at the end.
- A bold label opens a part only when it names one (Question, Context, Background, Why owner-only, Options, Recommendation, Blocks): `**A:** ...` under Options is text of Options, and counts as an option.
- A plain label (`Options:`) opens a part only in a body that writes none of its parts as a heading or a bold label. In a bold-label or heading body, a prose line led by `Question:` or `Background:` is prose.
- Only a heading named Log ends the body; a `Log:` line, plain or bold, is prose.
- An option is a list item, a `###` heading, or a line led by a bold label. A list item indented to the text of the item above it (CommonMark's nesting column), or past it, is that item's sub-bullet; a list under a `###` or bold option is that option's text. Tabs count as four columns.

**Options weighed.**
- For the remedy: make ask_parts read past the Log (rejected: the Log is history and holds any words, so an entry quoting `Options:` would be read as a part); change the remedy text to "edit its body" only (rejected: the remedy then names no operation, and `task section` would still bury a section under the Log for every other board item); insert above the Log (chosen: one place, and every board item keeps its Log last, as `task show` and the runbooks assume).
- For indentation: options at column 0 only (the scout's reading; rejected: a list indented one to three spaces, valid markdown, would count as no options); the shallowest indent in the part (rejected: it misreads a one-space sibling, which markdown reads as a sibling); the nesting column of the item above (chosen: markdown's own rule).
- For plain labels: a plain label that repeats a part already open is prose (considered; not taken: it does not cover a first `Question:` in prose, and adds a rule); body style decided by its labels (chosen).

**What stays unread.** In a body of plain labels only, a prose line led by a part's name still opens that part: only the writer knows it is prose (ask_problems says so under "Not checked"). A bold-led line under Options that is a note, not an option, counts as one, as a list item that is a note always has.

**Reopen if:** an open question that states its three parts is refused or failed by G-W4 under these rules, or one that lacks a part passes.

Task: CE-158.

## Amendments

- **2026-11-07d (claude-code/claude-opus-5-5):** CE-158 fix round 1 (agent's call under P8, claude-code/claude-opus-5-5, session 2026-11-07d; not owner words). The verifier found the option rule above passed a question with one option and refused one with two: a bold-led line counted as an option wherever it sat (`- A. ...` then `  **Why:** ...` read as two options; `### A` then `**Pros:**` and `**Cons:**` as three), and a bold line took every list item after it as its own text (`**Pick one**` above `- A` and `- B` read as one option). The "Reopen if" above was met. The rule now (guards.py::ask_options):

  - The options are the list items and `###` headings under Options. Only where it has neither (placeholders aside) are the bold-led lines the options, so a bold intro or note beside a list (`**Pick one**`, `**Note:** ...`) is no option.
  - A bold-led line follows the same nesting rule as a list item: indented to the text of the item above it, it is that item's text; under a `###` option, it is that option's text.
  - A bold line owns only what is indented past it: `**A:** ...` with `  - detail` under it is one option, and a list at the bold line's own column after `**Pick one**` is the options.

  Options weighed: a bold line owns nothing, as CommonMark nests no list in a paragraph (rejected: a bold option with indented detail bullets would read its first bullet as the only option); a bold line owns everything after it, as before (rejected: it is the false refusal found). Left unread: an intro written bold with its list indented under it (`**Pick one**` then `  - A`) reads as one option, the bold line; write the list at the bold line's column. "What stays unread" above now holds only where Options has no list item and no `###` heading.

- **2026-11-07e (claude-code/claude-sonnet-5-5):** **2026-11-08 (claude-code/claude-sonnet-5-5):** CE-201 (agent's call under P8, claude-code/claude-sonnet-5-5, session 2026-11-07e; not owner words). CE-158's verifier left two ambiguous Options shapes for "decide whether either is worth a rule". Both meet the reopen condition above (shape 2 is a false refusal, shape 1 a false pass), but no new rule is made; both are pinned by test as they read and listed under ask_problems' "Not checked" and in the ask_options docstring (guards.py::ask_options, guards.py::ask_problems):

  - A bold option with unindented bullets under it (`**A:** read` then `- x`, `- y`) reads as those bullets: it passes, with the options x and y. This is how CommonMark reads it (a paragraph, then a separate list).
  - Bold options beside an unindented list item (`**A:** ...`, `**B:** ...`, `- note: ...`) read as that list: one option, so it is refused. The refusal is visible, and its message now says "one list item or `###` heading each, or one bold-led line each where it has neither"; the fix is a cheap rewrite (indent a note under its option, or write the options as list items).

  Options weighed: take the larger of the list-item and bold readings (rejected: it fixes shape 2 but makes `**Note:**` plus `**Caveat:**` plus one list item pass as two options, a new false pass, and shape 1 still passes falsely); let bold lines before the first list item own that list (rejected: it breaks the tested `**Pick one**` and `**Note:**` cases above a list, the false refusal CE-158 round 1 fixed).

  Tested by tests/test_working.py::test_ask_options_reads_bold_lines_only_where_options_has_no_list_item_or_heading, and the placeholder clause (a placeholder-only list item such as `- <option>` hides no bold options) by a case in ASK_MISREAD. AC-121 is rewritten to this rule through `criterion set`. Task: CE-201.
