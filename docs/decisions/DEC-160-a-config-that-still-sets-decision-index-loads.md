---
type: Decision
id: DEC-160
title: A config that still sets decision_index loads; nothing reads it, and orient names the key and the stored file to remove
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
tags: [adoption]
tasks: [CE-185]
decided: 2026-11-06
session: 2026-11-06a
body_sha: sha256:51cea84e337cf3b86269912aee38dcdd2162dee4dbae7d5c55e2a81ba6d346ce
---

**Call** (agent, CE-185, on US-19): an adopting repo that still sets `[working] decision_index` keeps loading after the upgrade, and is told what to remove; nothing refuses and nothing goes red.

- `config.py` still accepts `decision_index` in `[working]` (an unknown key refuses, so dropping the field would make every adopter's `context.toml` fail to load). Nothing reads it: no write regenerates an index, `hk run close` runs no index step, and lint has no index check. The refusal for `decision_index` without a `decision` kind is gone with it.
- `G-D6` stays a guard id lint knows, so a `[guards] off` list naming it still loads; it reports nothing in the engine now.
- Orient shows a `Deprecated config: tell the owner` section while the key is set, naming the key and, where it exists, the stored file to `git rm`, and pointing at `decision index` and `site build`.
- The kit's `context.toml` template no longer sets the key, so a new adopter never gets one.

**Alternatives considered.**
(a) Drop the key, so a config naming it refuses to load. Rejected: an upgrade would break every adopter at once, before anyone reads why.
(b) Keep it and have lint (G-D6) fail while it is set. Rejected: the adopter's gate would go red on upgrade, and `context-engine commit` refuses a code path until the gate is green, so the upgrade would block unrelated work for a file that only goes stale.
(c) Delete the adopter's stored index for them. Rejected: deleting a tracked file in another repo is that repo's owner's call.

**Residual:** an adopter's stored `index.md` goes stale until someone acts on orient's notice (CE-185's design review).

**Reopen if:** an adopter's stale index misleads a reader, or the next contract bump is the moment to make the key refuse.
