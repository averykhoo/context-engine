---
type: Decision
id: DEC-248
title: "CE-190 ledger half: a grant writes a `granted:` stub bullet, carried as a close receipt; `session close` refuses a summary that does not quote each grant's words (whitespace-collapsed); the engine writes no summary line (DEC-178's reasons); a grant then a pause or abandon is Not checked"
actor: claude-code/claude-opus-5-5
refs: [DEC-162, DEC-178]
tasks: [CE-190]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:0df6efc00d866ea1c236cc29747a2a922108bcdf34d3e20b7644d5855d756182
---

Ruled at build time under DEC-162, which puts the owner's words of a one-off permission on the ask record and in the ledger `summary:`.

A grant writes a `- **granted:** ASK-n[, ASK-m]` bullet into the session's ledger stub, as `ask raised` writes `asked:`, and `session close` carries it as a `granted:` receipt. The close is refused when its summary, joined and whitespace-collapsed, does not contain each grant's words, also whitespace-collapsed; the remedy names the exact line to add (`ASK-n granted: "<words>"`). The engine never writes a summary line itself, for DEC-178's reasons: the closer authors the digest, the summary is capped at 1 to 7 lines, and an engine-written line could meet the close's own prose refusal.

Rejected: the words only in an engine-written receipt (orient's digest reads `summary`, not receipts); an id-only summary check, which leaves the words, what DEC-162 asks for, to discipline; an at-rest lint of the summary quote, left Not checked because the ask record holds the hashed words.

Not checked: a grant followed by a session pause or abandon (a pause entry carries no receipts or summary; the ask record still holds the words); whether the words really are a one-off permission.
