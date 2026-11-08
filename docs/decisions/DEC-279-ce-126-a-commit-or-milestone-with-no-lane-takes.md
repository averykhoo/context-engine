---
type: Decision
id: DEC-279
title: 'CE-126: a commit or milestone with no lane takes only unlabelled lines; no new commit flag, and --sweep is unchanged'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:af86cac7b784490fcf56fc55b93905a27c7ad987ede9056e462f0ad4462640af
---

The agent's call on CE-126, building DEC-84's option B in session 2026-11-07e: what a commit with no lane takes.

A commit or milestone made with no lane (the coordinator's) takes only the session's unlabelled lines, plus, as before, any line naming a path the commit carries. A lane's commit takes only that lane's lines on the same rule. No new commit flag is added: a dead subagent's lines are taken by the session's close or pause (every lane), and `--sweep` stays as it is, taking every line of every session, for a session known dead.

Rejected: the coordinator taking every lane on every commit (it brings back the mis-filing of 292541d the other way round, and sweeps a running subagent's half-done writes into the coordinator's commit); a `--lanes` commit flag (nothing needs it that the close does not cover).

Cheap to undo: one comparison in `commit.py::select`.
