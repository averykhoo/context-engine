---
type: Decision
id: DEC-1
title: The engine lives in its own repo and its own env, and is pointed at target repos
actor: owner + agent
decided: 2026-10-08
session: 2026-10-08a
decision_status: BUILT
tags: [packaging]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-08T15:00:00+08:00 }
body_sha: sha256:f935c9e8dc93eb6b6cd7f3dddc0f9a3d71deb620c52c4293a9ed0fcc91867b21
---

The agent proposed and the owner approved (*"Yes to all"*): the engine is written in **Python**
(owner: *"We can assume it'll be written in python"*), in its own repo
`PycharmProjects/context-engine` (private on GitHub, `averykhoo/context-engine`), with its own
conda env `context-engine` on Python 3.12.

**It runs from its own env and is pointed at a repo; it is never installed into a target repo's
environment.** A target repo's `.mcp.json` names the engine's interpreter, and the server takes
the repo root from its working directory (verified, `spike/FINDINGS.md`). Target repos are
node (audio-workspace), uv (SpeechEnhancement) or conda, and a research env should not carry
the MCP SDK.

Rejected: building it in `.scratch/` (gitignored, no history, no backup) or inside the trial
repo (engine changes would mix into adhoc's history and gate, and the next repo would get a
copy, the divergence FRAMEWORK §0.2 warns about).

Consequence: if a target repo's CI is to run the lint, CI must install the engine, so this repo
needs to be reachable from that CI (private repo: a token).

## Amendments
