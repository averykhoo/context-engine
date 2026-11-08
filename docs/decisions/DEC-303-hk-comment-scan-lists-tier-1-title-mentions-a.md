---
type: Decision
id: DEC-303
title: 'hk comment --scan lists tier-1 title mentions: a Session commit whose title names an open task other than in its leading ids gets a tier 1 skip line'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:b4c8e134346a8224a09157af2524814286668f249184cec6faa229603d52042e
---

**Decision:** `hk comment --scan` (working.py::Engine.hk_comment_plan) lists a commit whose message carries a `Session:` line and whose TITLE names an open task (not a question) other than among its leading ids as one skip line per such id: `<short sha> <id>: tier 1: the title names <id> but does not lead with it (`hk comment <id> --commit <short sha> --text "<what it did for <id>>"`, or nothing): <subject>`. Nothing is written for it. The line is silent when the commit's `Closes:` trailers name the item or the item's log already cites the hash. Commit bodies are not scanned, and the foreign listing is unchanged: a commit with no `Session:` line is listed as foreign only when its title leads with an open id. `hk run start` shows these lines as `  - not done: ...`.

**Why:** FRAMEWORK §6.11 gives tier 1 the commits that name a task other than by leading with its id, and before this no `hk_` tool showed them (the plan skipped every commit whose title does not lead with an open id), so an agent limited to `hk_` tools had nothing to find. The plan and the run stay one code path.

**Rejected:** a separate read-only `hk_candidates` op (a second code path); scanning bodies (noisy: bodies cite many ids; the spec and procedures say "title"); widening the foreign listing (nobody asked for it).
