---
type: Decision
id: DEC-41
title: A target repo's engine env is a pinned install kept inside that repo's folder
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-14
session: 2026-10-14d
body_sha: sha256:1c95f0c84124b349524d94b9e0c7d0ea8f2d219c9cd88746279ebec6a21f8c50
---

Owner, 2026-10-14d, verbatim: "the engine should run within the adhoc repo so thats where everything should exist."

Asked whether that means (a) a pinned engine env of its own stored inside the adhoc repo's folder, (b) installing the engine into adhoc's own conda env, or (c) vendoring the engine source into adhoc, the owner chose (a): "Own env, in adhoc folder (Recommended)", described as "A pinned, non-editable engine env stored inside the adhoc repo (e.g. <adhoc>/.context-engine/, gitignored). Everything lives in adhoc, the engine stays out of adhoc's research env, and kit changes here can't break adhoc's lint. DEC-1 gets amended (where the env lives), not overturned."

So for a target repo, the engine's env is a pinned (non-editable) install of a fixed engine commit, kept inside that repo's folder and gitignored, separate from the repo's own environment. This amends DEC-1 on where the engine's env lives; DEC-1's rule that the engine is never installed into a target repo's own environment stands. It also settles CE-7's pin trap (dry run F18): kit changes made in the engine repo mid-trial do not reach the target repo until its pinned env is upgraded.
