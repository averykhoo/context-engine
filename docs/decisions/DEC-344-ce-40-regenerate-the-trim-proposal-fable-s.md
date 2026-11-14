---
type: Decision
id: DEC-344
title: "CE-40: regenerate the trim proposal; fable's verdict APPLY WITH CHANGES, four made; the paste waits on the owner"
ruled_by: claude-fable-5-1
actor: owner asked
decided: 2026-11-14
session: 2026-11-14a
decision_status: PROVISIONAL
body_sha: sha256:e62ffe402997dcd61b44699f3f77c91dad2c6d84980bc5ccef84737636d0ff6e
tasks: [CE-40]
---

Owner, 2026-11-14a (DEC-343 item 6), on CE-40's stale trim proposal (regenerate it, or drop the trim): *"6 - I'll leave it to you or fable"*

## Ruling

1. **Regenerate the proposal, do not drop the trim.** The 2026-11-07e proposal was drafted against a 411-line global file; the live file is 456 lines, with three insertions only (§ Gemini API key, § Hugging Face token, CE-110's two Assurance-traps bullets). The refreshed proposal is docs/evidence/global-claude-md-audit-2026-11-14a.md § 4. Every line of the seven machine sections survives verbatim, checked mechanically and sabotaged five ways. The two CE-110 rules are GAP (no framework text holds them) and stay.
2. **fable's verdict: APPLY WITH CHANGES.** Four changes, made in § 4: the baseline heading drops "(optional: delete ...)"; the Docker pointer names § Repos without the framework; the 2026-09-20 standing approval for read-only agents and the Workflow tool is kept in the baseline, its only other home being contract.md, which a repo without the framework never reads; the dated "user instruction" markers and the CI watcher's return shape come back on three baseline bullets.
3. **Applying § 4 to ~/.claude/CLAUDE.md waits on the owner's yes.** The edit is outside the repo and rewrites the file every session on the machine reads, so it is not an agent's call (contract, Who decides; DEC-342's list, condition 3). When applied: back up the live file to ~/.claude/CLAUDE.md.2026-11-14-pre-trim.bak first (live sha256 9798980e...01bf), then close CE-40.
