---
type: Decision
id: DEC-6
title: "First trial repo: adhoc-microphone-array; intervals second"
actor: agent (claude-opus-5-5)
decided: 2026-10-08
session: 2026-10-08a
decision_status: PROVISIONAL
tags: [adoption]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
---

The owner named two candidates (*"I'm thinking intervals or adhoc first"*); the agent picked
adhoc, on a survey taken 2026-10-08:

- adhoc's tree was clean; intervals had 24 uncommitted files from a live session mid-D32 and is
  heading to its 2.0.0 release (H1, blocked on Q25).
- adhoc gains most: an inline board of about 16 rows with sub-ids (1, 1a, 1b, 1d, 1f, 1g, 1e,
  2 to 8), a 28 KB HANDOFF with a ~60-line banner and the session log inside it.
- adhoc's 33 decisions (`docs/decisions.md`, 52 KB, D-1 to D-33) already carry actor and date in
  their headings and have a "Built and rejected" section: a cheap, honest test of decisions as
  records.

intervals goes second, after 2.0.0: it tests the library criteria path and repo-specific id
formats (`D32`, `Q26`), and is the busier repo (185 commits in 14 days against adhoc's 47).
PROVISIONAL until the owner confirms, which the board does not block on.

## Amendments
