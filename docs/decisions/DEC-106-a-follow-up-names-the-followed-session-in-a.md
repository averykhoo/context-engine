---
type: Decision
id: DEC-106
title: A follow-up names the followed session in a follows bullet, not a digest line
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:f77b27b2e0ba7594b81dabbf2a4db4f8a162c124aab98e6aa672c3d792e6ebb3
---

The agent's call on CE-84, made while building it in session 2026-10-30a: how "the close digest names it" (DEC-45) is met.

Options:
(a) a `- **follows:** <key>` bullet first in the close (and pause) entry; orient shows the followed session's rows, digest and still-owed lines in a rank-1 part; the op log's session.start fields stay ["kind"];
(b) a generated summary line in the digest.

Chose (a): a summary line would count against the 7-line digest cap.

Built in lane commit f88f624, on main as 7920cbd (ledger.py::FOLLOWS, ledger.py::render_close, ledger.py::render_pause); pinned by AC-123. Cheap to undo.
