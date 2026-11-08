---
type: Decision
id: DEC-251
title: "CE-196: register retire keeps the entry: heading `(retired <session>: <why>)` plus a last `retired:` line (INV-97's hand form); never deleted, never undone"
actor: claude-code/claude-opus-5-5
tasks: [CE-196]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:1b7e72cf2357b5d52b8b3ddabd6cb4b62c6bdf593d8cdf48391f471af05a7703
---

A build-time call for CE-196, the agent's own, PROVISIONAL until the owner reviews it.

`context-engine register retire <id> --why <why>` keeps the entry in the register. Its heading becomes `## <id>: (retired <session>: <why>) <risk>`, and the line `- **retired:** session <session> (<actor>): <why>; kept so its id is never reused` is added after the entry's last field line. That is the form INV-90 and INV-97 were given by hand on 2026-11-06c. An entry is never deleted, because FRAMEWORK P3 and §7.4 say an id is never reused. A retirement is final: the op refuses an entry that is already retired, and no op undoes one.
