---
type: Decision
id: DEC-130
title: An op log line may carry as, mapping a session-keyed field to the key it was set to; G-W7 checks the field against it (hk.stamp_asked)
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:33e62945e3396be0c4df5ad532c3a958dc26cc1d8bdc044e40bad1ff73ecd52e
---

The agent's call on CE-6, made while building `hk stamp` in session 2026-10-30a: how a housekeeping write that sets a session-keyed field (an open question's `last_asked`) to a key other than the writing session's passes G-W7.

Options:
(a) log the stamp under the receipt's own session. This breaks commit's selection of a session's own op lines, and it resets that key's staleness window;
(b) stamp the current session's key. This falsely says the question was raised now;
(c) an `as` key on the op line, mapping the session-keyed field to the key it was set to.

Chose (c). `hk stamp` sets each open question's `last_asked` to the newest finished ledger entry whose `asked` receipt names it, only where that is newer, as a mechanical write whose op line records the stamped key under `as`. G-W7 checks `last_asked` against that key, so the stamp passes and a hand edit still fails.

Built in lane commit 1812238, on main as 3fc1dbe. Links: CE-6, G-W7, AC-166, store.py::Store._log. Cheap to undo: a local commit and one optional op-line key.
