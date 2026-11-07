---
type: Decision
id: DEC-174
title: Owner decisions recorded PROVISIONAL before CE-187 are migrated by decision accept --owners
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-187]
decided: 2026-11-07
session: 2026-11-07d
body_sha: sha256:563816c2c5f8168ebbba688ee9823058aac98bce3a28d3b7c918a01eb927bdc9
---

An agent's call under P8 (cheap to undo), made by CE-187's builder in session 2026-11-07d. Not owner words.

**Call.** The owner-actor decisions recorded PROVISIONAL before CE-187 move to ACCEPTED through the op, as a one-shot migration: `context-engine decision accept --owners`. The flag selects every decision still PROVISIONAL whose actor is the owner's own (`owner` or `human:<id>`, any case) and that has no `ruled_by`, and accepts them all in one write and one `accept` op line. It can be given in the same call as DEC-162's list of agent calls, so one op line carries the whole migration.

**Options weighed.**
- A read-time rule (an owner-actor PROVISIONAL reads as ACCEPTED): rejected. Every reader of `decision_status` (find, index, the site, orient, lint) would have to apply it, and the files would keep saying PROVISIONAL, so a reader of the raw record is misled.
- A one-shot migration outside the op (a script, or `decision set` per record): rejected. It writes no `accept` line, or one `set` line per record, which is the op-log noise DEC-162 ruled out.
- The op, with a selector: chosen. The files say what is true, one op line records the migration and who ran it, and an adopting repo runs the same command once after its upgrade (kit README § 4).

**What stays.** Agent calls (their own actor, or `ruled_by`) are never selected by `--owners`; they are accepted only by id after the owner's review. A repo whose `context.toml` enum still lacks ACCEPTED keeps recording owner decisions PROVISIONAL, and G-D0 names the missing value.

**Reopen if:** the sweep accepts a decision that was not the owner's own words (a hand-written actor), or the owner wants owner decisions reviewed before they read as accepted.

Task: CE-187.
