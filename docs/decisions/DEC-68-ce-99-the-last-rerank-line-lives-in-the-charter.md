---
type: Decision
id: DEC-68
title: 'CE-99: the last-rerank line lives in the charter; task goals are a G-I1 check on open tasks'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
decided: 2026-10-20
session: 2026-10-20e
body_sha: sha256:2068f0bfa19bc2a60fa23fbd8ba3592d9864357bd580bcf82e70fef3c32b6b1d
---

The agent's call (cheap to undo, FRAMEWORK P8), made while building CE-99 under DEC-64 and its 2026-10-20b amendment.

**Where the rerank's trigger state lives:** a `Last rerank: <session key>` line (or `Last rerank: never`) in `docs/charter.md` § Next milestone, beside the milestone it ranks against. The rerank (procedures.md § Rerank) rewrites that one line, the one edit to the charter that needs no owner; `context-engine orient` reads it and says "rerank due" when an owner decision or story is newer than it.

**How the task goals are checked:** `[guards] task_goals` names the board kind whose open items must carry `goals` (G-I1, the same check as a story's goals, standard `G-n` form only). It is a guard, not a `required` key of `[kinds.task]`, because the schema check reads closed tasks too, and closed tasks are history filed before tasks carried goals. `task new --goals` and `task set --set goals=[...]` refuse a goal the charter lacks; housekeeping's expired-baton tasks are not refused (housekeeping makes no judgement call) and G-I1 flags them.

**What "newer" means:** an owner record (`actor: owner` or `human:<id>`) of the decision or story kind whose `session:` key sorts after the last rerank's key; a record with only a date counts as newer when its date is after the rerank's date. Amendments are not read (an owner amendment that changes priorities is the coordinator's to flag, or the owner's to ask for).

Why: the charter already holds the goals and now the milestone, so the rerank reads one file; a separate state file or a ledger field would be one more thing to route and lint. Undo: move the line and point orient at the new place.

## Amendments

- **2026-10-20f (claude-code/claude-opus-5-5):** Superseded in part by DEC-64's 2026-10-20f amendment (owner: "Rerank should only run when next is empty"). Orient no longer reads the `Last rerank:` line as a trigger: "rerank due" fires only when NEXT holds no task while tasks are open. The charter keeps the line as a record of when the last rerank ran (the rerank still writes it, procedures.md § Rerank step 5), and orient quotes its value after the reason. The section "What 'newer' means" no longer applies: the newer-owner-record trigger, and the missing / `never` / not-a-session-key triggers, are removed (`guards.py::owner_mark` and `guards.py::newer_than` with them). The task-goals part (G-I1, `[guards] task_goals`) stands unchanged.
