---
type: Decision
id: DEC-304
title: 'A tier-1 text comment carries its sha: hk comment --text logs <short sha>: <text> unless the text already cites the hash'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:3fce856777bb668474bbcc5a16771ee51134ed0e49c357e46282da03790ad72d
---

**Decision:** `hk comment <id> --commit <sha> --text "<words>"` (working.py::Engine.hk_comment) logs `<short sha>: <words>` unless the words already cite a prefix of the commit's hash (a `ledger.SHA_RE` match that the full hash starts with), in which case they are logged as given. The prose checks run on the text as logged.

**Why:** the scan's "log already cites <sha>" check is what keeps a second run from commenting twice; a tier-1 comment that did not carry its hash was invisible to it, so a second tier-1 run would comment the same commit again. An engine rule is cheap and holds where a prompt rule ("start your text with the sha") would not.

**Rejected:** a prompt-only rule in the agent's instructions (a doc warning where a mechanical rule is cheap).
