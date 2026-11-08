---
type: Decision
id: DEC-286
title: "coverage: an open board item does not outrank the map's DEFERRED or PROSE-ONLY (G-T4 is only mentioned in passing by CE-34; CE-168 is where G-V2's deferral is kept); a stale row is cleared by built outranking the map, or by a new dated map"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:6f863b2f96ece50fcd3bcf9838ef8b1db953d691d5e1804d69b9d3f323512676
---

The agent's call on CE-164 (session 2026-11-07e): in `context-engine coverage` an open board item does not outrank the newest map's DEFERRED or PROSE-ONLY row. The rule order stays: built, then deferred and prose-only, then open work, then done.

CE-164's second residual read the order as a bug (G-T4 reads deferred though open CE-34 names it). It is not: CE-34 (G-T5, mutation) names G-T4 only in passing ("G-T4 substitutes"), §11.2's trigger for G-T4 is not hit, and the 2026-10-30a rerank row for CE-34 asks that the map say deferred. Likewise open CE-168 is where G-V2's deferral is kept. A board mention cannot tell work from an aside, so it must not un-defer. A stale DEFERRED row is cleared instead by built outranking the map (the G-W10 case, the ENFORCED decision) or by a new dated map. A test pins the order.

Cheap to undo: the order is the order of clauses in `guards.py::_item_status`.
