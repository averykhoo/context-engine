---
type: Decision
id: DEC-114
title: Build CE-144 (the optional ambiguous-bare-name check) rather than drop it, in G-D3 only
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
decided: 2026-10-31
session: 2026-10-30a
body_sha: sha256:f070177beb9e7e4af57ac309744f9df3fec66308303ac451716defcdcebce8b4
---

The agent's call on CE-144, made while building it in session 2026-10-30a.

Options:
(a) drop the task, as the owner allowed;
(b) build it in G-D3 only;
(c) build it in G-D3 and G-T3.

Chose (b). It was cheap and adds zero false reds. A 2026-10-30 census of the links docs found 69 bare-name spans that match two or more files, every one a byte-equal pair. It also stops a `file::symbol` from being checked against whichever file happened to come first. G-T3 is left unchanged, to keep the task to its brief, and its docstring now says so.

Built in lane commits b5adfb3 and 339091e, on main as 1a6a059 and 4ca385f. Cheap to undo: revert those commits.
