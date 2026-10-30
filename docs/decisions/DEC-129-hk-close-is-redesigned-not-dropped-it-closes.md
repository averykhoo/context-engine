---
type: Decision
id: DEC-129
title: 'hk.close is redesigned, not dropped: it closes only on a git-checked Closes: trailer of a commit made outside the engine, or on a finished ledger entry naming the item closed, and a reopen outweighs either'
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:f45648d16437859e9f211112f2ec236d9563222dfe7e680b8a6d48a291cece46
---

The agent's call on CE-6, made while building it in session 2026-10-30a: what `hk.close` is, after the 2026-10-13b review suggested dropping it.

Options:
(a) drop `hk.close`, and make a `Closes:` trailer that names a still-open task a lint red (the 2026-10-13b review's suggestion);
(b) keep it as specced: close on commit or ledger evidence, with no scan;
(c) keep it, redesigned.

Chose (c). Under (c) a commit counts as evidence only if all four hold: it is in HEAD's history; git parses its trailer as `Closes: <id>`; the item was not already closed in that commit's own tree; and the item's Log does not already cite that commit. Ledger evidence is a finished entry whose `rows:` says `<id> (closed`, and it counts only while the item's Log has no close line from that entry's session and no reopen from a later session (review fix af963f2, after the 2026-10-30a review). A `--scan` closes every open task a trailer names, never an owner question, and lists the ones it could not close with the reason.

Why (c): FRAMEWORK §6.10 item 1 says a commit made outside the engine that finishes a task carries `Closes:`, and housekeeping then closes the item, so `hk.close` has a real subject; the engine's own close commits already carry their trailer. Option (a) would stay red forever after any reopen, because the old close commit keeps its trailer. Under (c) a reopen outweighs both an old trailer and old ledger rows. G-W9 re-checks the evidence against the log before the close line, so a later reopen does not turn an old close red.

Known gap (from the re-verify): the later-reopen rule orders sessions by start order (store.py::key_order), not by when the reopen happened. If a third session closes the item, and a concurrent session keyed before the ledger entry's session then reopens it, an entry whose rows name it closed (though that session never closed it) would let `hk close --ledger` close it again. This needs rows naming a close the session did not make, so it is narrow.

Built in lane commits 1812238 and af963f2, on main as 3fc1dbe and f498178. Links: CE-6, FRAMEWORK §6.11, G-W9, AC-20, AC-165. Cheap to undo: local commits and lint.
