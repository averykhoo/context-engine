---
type: Story
id: US-10
title: Long tests run as separate tiles, and each result is tied to a hash of the code, so new sessions know what is already tested
actor: owner
via: Claude Code chat session 2026-10-08b
date: 2026-10-08
story_status: live
goals: [G1, G7]
body_sha: sha256:3d526e0975cb047cc214e206906ddee928343687be73ba0dcd7f679d2d72155e
---

## Owner's words (verbatim)

> splitting long running tests into tiles and running them separately (maybe in parallel) is
> another pattern thats good, and the tests should tie their status to a hash of the repo code,
> so that new sessions can figure out whats tested or untested and not need to rerun it all
> again if it is all already tested, is that in here

## Notes

AGENT: partly. FRAMEWORK §8.5 G-V1 (run ledger) keys gate phases on the content tree id
(intervals `tools/gate.py`, zanzibar `gate_status.py`). Missing: tiles; keying each tile on the
hash of its own inputs rather than the whole tree; `orient()` reporting tested and untested;
and a generic implementation (§8.0.1 leaves verification state to zanzibar). Filed as CE-17.
