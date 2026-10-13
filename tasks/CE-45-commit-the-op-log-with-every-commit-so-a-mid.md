---
type: Task
id: CE-45
title: Commit the op log with every commit, so a mid-session commit passes lint alone
brief: A clean checkout of any commit before the close is red on G-W7; a dead conversation leaves op lines uncommitted
pri: NEXT
state: closed
deps: []
source: session 2026-10-13b
created: 2026-10-13
moved: 2026-10-13c
updated: 2026-10-13c
review: [write-op, git-loss, shipped]
status: deprecated
closed: 2026-10-13c
---

Found 2026-10-13b: per-task commits (2026-10-13a's too) leave docs/ledger/ops.jsonl and the session stub uncommitted until session close, so a clean checkout of any mid-session commit fails lint (G-W7 reads a task's moved against ops.jsonl), and a conversation that dies leaves its op lines dirty in the shared tree for another session's close to sweep up. Options: each engine write commits its own op line by path (FRAMEWORK §5.5 rule 4, today only pause open does); or rituals require the op log in every commit; or G-W7 tolerates an op log behind HEAD. Recommendation: the engine commits its own working-state writes, as §5.5 already intends, with the ritual as the by-hand fallback. 2026-10-13b worked around it by committing ops.jsonl with its commits.

## Log

- 2026-10-13c (claude-code/claude-opus-5-5): 2026-10-13c: owner asked for the NEXT items this session (adhoc has a live agent, so CE-7 waits). Building on branch ce-45 in worktree context-engine-wt/ce-45, taking the item's recommendation (the engine commits its own working-state writes; the ritual is the by-hand fallback).
- 2026-10-13c (claude-code/claude-opus-5-5): Built 2026-10-13c in worktree ce-45 (build; false-pass, false-red/deploy and spec-fidelity lenses; a skeptic; fix), rebased onto CE-26 and fast-forwarded: 5eea8c0, 83bb768, 9adbe72. Took the item's recommendation: each engine write commits by path under the lock, sweeping every op line HEAD lacks with the files it names; [engine] commit = false is the off switch, a pause commits regardless; .gitattributes unions ops.jsonl. Review: 23 findings, 22 confirmed and fixed (C21 partly), 1 rejected. Gate on main: 543 passed in 150.09s. First-hand sabotage: commit.py::new_lines returning [] -> 22 tests in tests/test_commit.py red. Flagged for the owner: CLAUDE.md § Gate and the kit contract say gate before every commit touching a record; the engine's own commits are now an exception (FRAMEWORK §5.5 and the kit README say so). Closed through the pre-restart MCP server, which still runs the old code and does not commit, so this close is committed by hand to carry Closes:.
- 2026-10-13c (claude-code/claude-opus-5-5): closed: done in 5eea8c0..9adbe72 (the engine commits its own writes by path, op log included; reviewed by three lenses and a skeptic; gate 543 passed)

## Design review

affects: every session in every repo the engine runs in, since each write now commits under the lock; other sessions sharing a working tree, whose uncommitted lines and files a sweep carries; the owner, whose history gains one commit per write; a plain-git human who commits by hand or merges branches carrying op lines
- eliminated: a clean checkout of a mid-session commit is red on G-W7 because the op log is committed only at close | rung: eliminate | control: commit.py::commit after every write, under the lock, sweeping every op line the tree has and HEAD lacks with the files those lines name; tests/test_commit.py::test_a_mid_session_commit_passes_lint_on_its_own runs lint on a clean clone
- reduced: a commit sweeps in another session's staged or untracked work | rung: reduce | control: git commit --only by path with --pathspec-from-file; git add only for new named paths, taken back on a failed commit
- reduced: the commit lands in the wrong repo (a target nested in an unrelated repo, GIT_DIR or GIT_INDEX_FILE set inside a hook) | rung: reduce | control: commit only when context.toml is tracked or staged; a loud skip when GIT_* variables are set
- reduced: a merge, rebase, cherry-pick, revert or bisect in progress, a detached HEAD, a refusing hook, a dubious-ownership refusal, a gitignored op log or missing git silently loses the commit | rung: reduce | control: each is a loud skip on the op's one line, with its by-hand step; a pause that cannot commit refuses and keeps its record (AC-14)
- reduced: a slow hook holds the lock past the git timeout and leaves index.lock behind | rung: reduce | control: git output goes through files, not pipes, so the timeout bounds the call; the note names a fresh index.lock
- reduced: two branches' op logs conflict on merge | rung: reduce | control: .gitattributes docs/ledger/ops.jsonl merge=union
- residual: a hook slower than lock_timeout (30s) makes other sessions' writes refuse while it runs | rung: individual | why: a commit hook's time is the repo's, not the engine's | control: they refuse before writing; the git call times out at 120s
- residual: another session's hand edit in progress to a file an op names (HANDOFF.md via banner set, a task body) is committed as it stands | rung: individual | why: telling an op's change from a hand edit in the same file is not cheap; the engine already rewrote the whole file before | control: the op's line names the sessions whose lines it carried
- residual: an error other than a Refusal partway through a multi-write op commits a half-made change silently | rung: individual | why: the commit runs on the lock's exit whatever ended the op | control: lint reports the half-made state
- residual: G-W7 cannot see an op line whose record is missing at HEAD, which a by-hand commit can make | rung: individual | why: no guard checks op lines against paths at rest | control: the engine never makes such a commit; manual-mode § Commit the write
- residual: a pause's uncommitted list is read before its own commit, so it can list paths that commit then sweeps in | rung: individual | why: the list is reported before the commit runs | control: the op's line names the commit's sha
- residual: merge=union can reorder or duplicate op lines from two branches, and G-W7 takes newest from file order | rung: individual | why: union merge does not order lines | control: lint after a merge; rituals § Foreign reconcile
- residual: every write is a commit, so history grows fast and each write costs about 0.5s under the lock on Windows | rung: individual | why: FRAMEWORK §5.5 rule 4 chooses a commit per write over a dirty tree | control: [engine] commit = false turns it off (a pause still commits)
- residual: an older engine refuses a context.toml carrying [engine] commit | rung: individual | why: kit version skew between repos | control: kit README upgrade step
- residual: under git's reftable format HEAD falls back to symbolic-ref, a path no test covers | rung: individual | why: no reftable repo in the test matrix | control: none beyond the detached-HEAD skip
F: goes stale when git's porcelain output, its in-progress markers or its env variables change, or when an op stops going through Op.call; the 43-row sabotage table (tools/sabotage_ce45.py) and tests/test_commit.py catch each
A: [engine] commit = false switches it off; every skipped commit says why and names the by-hand step in manual-mode § Commit the write; a by-hand commit by path does what the engine does
M: one function, commit.py::commit, called from Store._lock on exit; Op.call appends committed <sha> or not committed: <why> to every op's one line, for CLI and MCP alike
E: reuses the store lock, the op log and git's own --only and --pathspec-from-file; reviewed by false-pass, false-red/deploy and spec-fidelity lenses plus a skeptic: 23 findings, 22 confirmed (C1 to C22, fixed; C21 partly), 1 rejected
