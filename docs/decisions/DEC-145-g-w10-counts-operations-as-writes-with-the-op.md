---
type: Decision
id: DEC-145
title: G-W10 counts operations as writes, with the op log lines beside them; the count line ends the reply
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-11-01
session: 2026-11-01b
body_sha: sha256:0524236bb98d825f4f7b9b83259a8b9836352511b961645bbaa7ca79dc3c0314
---

The agent's call on CE-6, made while building G-W10's counts in session 2026-11-01b: what G-W10's "writes" counts, and where the count line goes.

Options:
(a) writes counted as op log lines, so an abandon that files a baton is 2 writes;
(b) writes counted as operations, so an abandon that files a baton is 1 write and 2 op log lines; the reply reports both, and the count line is the reply's last line, after the 'not done' line.

Chose (b): the `[housekeeping] max_writes` cap is checked against the plan before any write, and the plan counts operations; the op log's gain is reported beside it so the two can be checked against each other.

Built in lane commit f12e59f, on main as 80e9407; pinned by AC-177. Cheap to undo: the count and the reply's line order.
