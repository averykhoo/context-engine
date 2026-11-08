---
type: Decision
id: DEC-323
title: "Rollback and close undoes records by their operations and files by path, never by revert, reset, stash or file restore; owner's word only; ends in a kind: close entry"
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-18, CE-215]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:a64b708ed71c2363e4fd482b6ae84e14e99c4b46be3f65e84305d6b4da3077f9
---

An agent's call under P8 (cheap to undo: FRAMEWORK §6.13 and the runbook section are edited in place), made by CE-18's builder in session 2026-11-07e on 2026-11-08, following the CE-18 planner's design. Not owner words; PROVISIONAL until the owner reviews it. FRAMEWORK §6.13 carries the design; these are its calls of consequence, with why.

1. **Records are undone through the operations that own them** (task reopen, promote, set, dep, section; decision set REJECTED with `reopen_if`, then record amend; criterion set retired; baton done or add; banner set), never by restoring or deleting their files. A record file put back to its old bytes fails G-W7 (`guards.py::tool_owned`: its `updated`/`moved` keys contradict the newest op line, which is the session's), and a record file deleted fails it too (`guards.py::op_records`: an op line names no file). Rejected: restoring the files and teaching G-W7 to accept a rollback op line; it still loses the record's history (a task's log).
2. **The op log and the ledger are never rolled back, and `git revert`, `reset`, `stash`, `clean` and `checkout <rev> -- <path>` are never used.** The undo is new op lines and new by-path commits (`git restore --worktree`, and `git apply -R` after `--check`). So G-W7 and G-D2 hold (`store.py::Store.created_ids` remembers ids through the op log), and other writers' index and lines are untouched. A revert would take back op-log and ledger lines that interleave with other sessions', write the index, and on a conflict leave a revert in progress, which makes every session's engine commit refuse (FRAMEWORK §5.5 rule 4). Rejected too: deleting the session's uncommitted op lines with their files, which frees ids that may already be cited.
3. **A rollback ends in a normal `kind: close` entry:** `rows:` say `rolled back`, and one summary line says `rolled back: <commits>; kept: <ids>; left: <paths or none>`. A `kind: rollback` entry is deferred with the engine operation (CE-215).
4. **A rollback runs only on the owner's word, after the owner has seen the plan** (including any untracked files it would delete). The agent may propose one. P8: discarding uncommitted work and deleting untracked files are not cheap to undo.
5. **A task or question the rolled-back session created stays open, with a comment** (the work is undone, not the need). It is closed as dropped only on the owner's word. Its id stays used either way.
6. **Scope: the session's own work.** A closed session's work is rolled back by a follow-up session (`session start --follows <key>`) running the same steps for that key. A file whose hunks overlap another writer's is left (Still owed and a baton), never forced.
7. **No contract change and no new frozen coverage map.** The runbook's map row and the plugin skill carry the procedure. Until the next map, coverage shows §6.13 as open work, owned by the deferred-build item.

Measured while building (2026-11-08, Git for Windows, `tests/test_rollback_recipe.py`, with `core.autocrlf` off and on): `git restore --source=<c>^ --worktree -- <path>` on a file the session created deletes it from the working copy and exits 0, leaving the index alone. The planner had expected it to fail. The runbook says the restore deletes the file, and the test pins it.
