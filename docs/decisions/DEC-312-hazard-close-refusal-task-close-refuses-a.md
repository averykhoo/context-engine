---
type: Decision
id: DEC-312
title: 'Hazard close refusal: task close refuses a `hazard`-labelled row whose close states no resolution (--residual risk line or none, or design-review residuals), mechanical/hk closes included'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:3ea89a2043107a7223c4fcf8c472f8b25d86f1d1b8c5128f88774b8ee86bae07
---

**Decision:** `task close` (and so MCP `task_close` and `hk close`) refuses to close a row labelled `hazard` unless the close states a resolution: `--residual <risk line>` (confirmed: filed in the register), `--residual none` (fixed or dismissed; the message says which), or a design review that lists a `- residual:` (filed at the close). Mechanical (housekeeping) closes get no exemption: `hk close --scan` lists such a row as not closed. The check sits in working.py::Engine.close's nested `check`, beside the existing `none`-against-review refusal.

**Why:** DEC-50 says a hazard row's close resolves it into a register entry, a fix or a dismissal. A mechanical refusal is preferred to a doc warning (FRAMEWORK P7), and housekeeping has no judgement to resolve a hazard with: a `Closes:` trailer is evidence the work was done, not that the hazard was resolved.

**Rejected:** docs only (leaves the rule unenforced); exempting mechanical closes (a trailer would close a hazard blind).
