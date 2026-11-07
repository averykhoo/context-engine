---
type: Decision
id: DEC-211
title: "an entry-less log's import refusal names its `###` headings: parse_log stays a pure reader, plan_import is the layer that refuses"
actor: claude-code/claude-opus-5-5
tasks: [CE-171]
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:e0a70fc901416db88c031a47191162d5c37951b4f7f13d57fb45c874b568cfcf
---

A log with no entry heading (`### <id> -- title *(actor, date)*`) is refused by `decisions.py::plan_import`, as it has been since CE-5, and the refusal now says why: how many `###` headings the log has outside code fences and comments, the first in full by line and the next ones by line (at most eight more), none of which starts with an id and a dash; or that it has no `###` heading at all. The remedy names the heading form to write in a copy (`*(unrecorded, <date>)*` when the log names no one).

`decisions.py::parse_log` stays a pure reader that refuses nothing for a text it can read with no entries in it: probes and tests call it directly (the CE-11 survey's "0 entries, exits clean" came from such a direct call, not from the import), and `plan_import` is the layer that refuses. An entry-less log is not a `Problem`, since no single line is wrong.
