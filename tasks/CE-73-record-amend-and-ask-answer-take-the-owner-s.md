---
type: Task
id: CE-73
title: record amend and ask answer take the owner's words from a file
brief: Intake puts words in a file, not a heredoc; two of the four intake commands only take an argument (audit 2026-10-14a)
pri: LATER
state: open
deps: []
source: session 2026-10-14a
created: 2026-10-14
moved: 2026-10-14a
updated: 2026-10-14a
review: [shipped, write-op]
---

record amend and ask answer take the owner's words from a file.

## Traps

- none yet

## Read first

- none yet

## Log

## Design review

affects: the owner, whose words must land verbatim; the session doing intake, which must not pass words through a heredoc
- eliminated: two of the four intake commands can only take the owner's words as an argument, against the rule that words go via a file
- reduced: both the argument and --file, or neither, are given | rung: reduce | control: cli.py refuses with a remedy (cli.py::WORDS); tests/test_working.py::test_record_amend_and_ask_answer_take_the_owners_words_from_a_file
- reduced: older argparse fills the optional positional too early and drops words given after an option | rung: reduce | control: cli.py::_parse puts one stray non-option argument back into the words; test_owner_words_after_an_option_land_even_where_argparse_fills_the_positional_too_early
- residual: ask answer wraps the words in `*"..."*`, so multi-paragraph words from --file render with stray asterisks | rung: individual | why: a blockquote would render well but the stored text would no longer be byte-verbatim | control: the words are stored verbatim; the rendering is cosmetic
F: stale when an intake command is added; it must take --file too (procedures § Intake lists them)
A: the words can be pasted into the record's body by hand (manual-mode § ask answer, § record amend)
M: one table, cli.py::WORDS, names the positional --file stands in for, and one check in cli.py::_params refuses both or neither
E: reuses record new's --file; reviewed by correctness, deploy/fresh-user and skeptic lenses
