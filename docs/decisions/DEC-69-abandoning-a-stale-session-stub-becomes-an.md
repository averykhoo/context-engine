---
type: Decision
id: DEC-69
title: Abandoning a stale session stub becomes an engine op, run by start-of-session housekeeping past DEC-29's window, without the owner's word
actor: owner
decided: 2026-10-22
session: 2026-10-22b
decision_status: PROVISIONAL
answers: ASK-18
body_sha: sha256:b9e0965f16b0b9455630980352fac7ba70b84359cbc0c1673000819e6a2d2a56
amends: [DEC-29]
tasks: [CE-124]
---

Owner, answering ASK-18: *"Owner, 2026-10-22b, answering ASK-18 (CE-124). The recommendation put to them was option 1: add `session abandon <key>` as an engine op; start-of-session housekeeping runs it on any stub past DEC-29's window (3 later closes or pauses after its last activity) and orient lists it in the digest; no owner word needed, since a stale stub has been shown to the owner at least 3 times by then.

"Okay to your recommendation for ask18""*
