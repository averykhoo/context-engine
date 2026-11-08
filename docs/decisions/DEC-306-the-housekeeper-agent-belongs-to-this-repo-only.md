---
type: Decision
id: DEC-306
title: The housekeeper agent belongs to this repo only (.claude/agents/), not the kit's or the plugin's (DEC-97)
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:5411ad5e01a0384bdd499a351e2f8f609d1de136c0af13290e0c1180eadd6ef6
---

**Decision:** the housekeeper agent is this repo's own, at `.claude/agents/housekeeper.md` (tracked; `git check-ignore` returns 1), and is not shipped in the kit or the plugin.

**Why:** DEC-97: the kit ships the agent roster as FRAMEWORK §6.6 text, not as named agents. An adopter writes its own agent file from the roster row and §6.11.

**Rejected:** shipping it in `src/context_engine/kit/` or the plugin (contradicts DEC-97, and the agent's model and prompt are this repo's choices).
