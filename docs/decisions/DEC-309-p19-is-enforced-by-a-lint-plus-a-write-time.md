---
type: Decision
id: DEC-309
title: P19 is enforced by a lint plus a write-time refusal that every manual criterion is named by an open board item, filed as CE-206; the residual half stays a design-review judgement
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:ce51a47e216e4e2777f6b959891dabd26b628bbc8b644d591277be09ed1bab86
---

**Decision:** what enforces P19 is a lint plus a write-time refusal (P7): every `manual` criterion is named by an open board item, and `criterion set --status manual` refuses one that no open item names. It is filed as its own LATER task, CE-206, and is not built in CE-194. The residual half of P19 (no hand-run check accepted as a residual) stays a design-review judgement (§5.2).

**Why:** a new guard needs §8 catalogue text, a guard id with a coverage-map owner (G-D12), a write-time refusal and its own sabotage; the census sized CE-194 small and docs-only. Today this repo has no `manual` criteria, so nothing goes unguarded meanwhile. A hand-run check described in a residual's prose is not mechanically recognisable: a lint over that prose would be text recognition, with false greens.

**Rejected:**
- building the lint inside CE-194 (scope; its own item);
- a lint over residual prose (false greens).
