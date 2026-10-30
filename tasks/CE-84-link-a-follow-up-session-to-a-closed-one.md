---
type: Task
id: CE-84
title: 'Link a follow-up session to a closed one: session start --follows <key> records follows: in its ledger entry, and orient and the digest show it'
brief: 'DEC-45. A framework edit, so the CE-7 freeze applies; no reopen: sessions stay append-only'
pri: LATER
state: closed
deps: []
source: session 2026-10-15a
created: 2026-10-15
moved: 2026-10-30a
updated: 2026-10-30a
goals: [G-1]
status: deprecated
closed: 2026-10-30a
---

Owner, 2026-10-15a (DEC-45): a session closed, then needed fixing. Today the follow-up is a new session with no link back (procedures § Clean close: 'More work asked for after the close starts a new session'). Proposed: session start --follows <key>; the ledger stub carries follows: <key>; orient and the close digest name it. Closed sessions are never reopened.

## Log

- 2026-10-30a (claude-code/claude-opus-5-5): closed: Done in 7920cbd (lane f88f624), cite in 87138ae: session start --follows <key> (MCP follows) refuses any key that is not a closed ledger entry and writes nothing; otherwise the stub, and then its close or pause, carry follows: <key>. Orient shows the closed session's rows, digest and still-owed lines to the follow-up, and ; follows on other sessions' lines. The closed entry is never touched. AC-123 tested; DEC-105, DEC-106.
