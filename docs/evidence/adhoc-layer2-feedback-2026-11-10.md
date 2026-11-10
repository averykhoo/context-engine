# adhoc layer-2 feedback: what the framework already ships (2026-11-10)

FROZEN: the audit as of 2026-11-10; the follow-up is CE-214 and CE-220..CE-223.

Session 2026-11-10b. The note below was pasted by the owner from the adhoc repo (an agent's note there, not owner words). Audit by a sonnet agent against the kit, FRAMEWORK.md, CLAUDE.md, the register and the board; the session filed CE-220..CE-223 and commented CE-214 from it.

## The note, verbatim

> What failed in layer 2, and the rule each failure produced
> Agent reports lost when the API dropped mid-run. Rule: every agent writes to its own file as it goes.
> Explore agents can't write files at all. Rule: use general-purpose agents for any persisted work.
> Messaging a running workflow agent created duplicates. Rule: answer it through a scratch file instead.
> Another session's commits swallowed 27 uncommitted files. Rule: commit by path; never git add -A or git stash.
> A PowerShell here-string (@'…'@) used in Bash gave a commit message of just @. Rule: pick the shell first, then write for it.
> Exit codes read through tail reported the pipe's status, so failures looked green. Rule: capture rc=$? directly.
> The 2026-10-17 crash came from backgrounded && chains. Neither ulimit -u nor taskkill /T stops Git Bash workers (AD-52). Rule: launch detached, cap workers at launch, and stop the job by process group, checked with ps.
> Detached bash used the wrong pdftotext. A detached bash -l picked up pixi's version, which would have silently rewritten text/. The version is now pinned (AD-75).
> Findings were lost from .scratch/ in another repo. That is why the salvage class exists.
> Today, ask20 wouldn't go to the Recycle Bin as a whole folder ("not supported"). Moving its contents one by one worked. The last attempt was then blocked only because my own shell was sitting inside the folder.
> One gap worth knowing: a fresh-clone gate skips about 180 tests that need local data. The skipped tests run only in the main tree.

## Audit

# Audit: adhoc note 2026-11-10 vs what the framework ships (read-only, 2026-11-10)

Prior intake: docs/evidence/adhoc-feedback-2026-10-21.md is a FROZEN copy of adhoc's earlier AAR (CE-7, closed 2026-10-21b); it produced CE-110 (shell rules, open SOMEDAY) and the persistence/watcher rules. Global ~/.claude/CLAUDE.md holds items 1,2,4,5,6,9 but does not count.

| # | Item | Verdict | Evidence / gap |
|---|---|---|---|
| 1 | Agents persist to own file as they go | INCORPORATED | kit/docs/runbooks/fan-out.md "Delegating reading and auditing": "Persist incrementally, one file per agent: each finding is appended as it lands, not buffered to the end"; kit/contract.md Rules: "every subagent persists its output to its own file as it goes" |
| 2 | Explore cannot write; use general-purpose | INCORPORATED | contract.md: "can persist (not `Explore`)"; fan-out.md: "Only an agent that can write files can persist (not `Explore`)"; FRAMEWORK §6.6 roster ("`Explore` ... since it cannot persist") |
| 3 | Messaging a running workflow agent duplicates it; answer via scratch file | MISSING | No hit for SendMessage / messaging a running agent in kit or FRAMEWORK. fan-out.md Workflows only says "passes the output by file" between runs. Portable (framework tells people to use workflows). |
| 4 | Commit by path; never git add -A / stash | INCORPORATED | contract.md Rules: "never `git add -A`, never `git stash`: sessions may share the working tree"; FRAMEWORK P12; fan-out.md worktrees |
| 5 | Pick the shell first (here-string in Bash gave `@`) | MISSING (kit) | Audit R2 (docs/evidence/global-claude-md-audit-2026-11-07e.md) classed it MACHINE. Only this repo's CLAUDE.md says "Write owner words to a file with the Write tool, not a heredoc" (not shipped). Portable core: pass multi-line commit text via a file (`commit -F`), write for the shell you chose. The table itself is machine-specific. |
| 6 | rc=$? not through tail | INCORPORATED | kit/docs/runbooks/gate.md "Running it": "Capture the exit code itself: `<gate> > <log> 2>&1; rc=$?` ... piped through `tail` or `tee`, a command reports the pipe's status" |
| 7 | Backgrounded && chains crashed machine; launch detached, cap workers, stop by process group, check with ps | MISSING | Nothing in kit/FRAMEWORK. CE-110 (open, SOMEDAY) only targets the owner's global file: rules 1,2 awaiting owner paste, rule 3 (`ulimit -u`) dropped per DEC-131 (docs/evidence/ulimit-gitbash-2026-11-01.md: errors in Git Bash). Process-group stop + ps check is new and portable (long jobs/watchers). |
| 8 | pdftotext pin (AD-75): detached `bash -l` resolved pixi's version | LOCAL for the pin; MISSING for the lesson | The pin is adhoc's. General lesson (a detached/login shell can resolve a different tool on PATH; pin tools whose output is committed, by path/version, and check which one ran) is portable and absent. |
| 9 | .scratch findings lost, hence salvage class | PARTIAL | Shipped: FRAMEWORK P10 ("anything recorded only there is already lost"), P11, fan-out.md "Agents audit; the session decides and deletes", "deletes the run's scratch files once their conclusions are in tracked files". Missing: the four classes and "SALVAGE is the deliverable", auditor's own dir excluded. Open task CE-214 (LATER) covers exactly this (R19, R20). |
| 10 | Recycle Bin refused whole folder; contents one by one worked; own shell cwd blocked it | LOCAL for the Windows quirks; MISSING for the portable line | Audit R21 classed MACHINE; DEC-320/CE-214 omit it. Portable core: sweep deletes must be recoverable (trash, not rm -rf) and the auditor never deletes. CE-182 log adds Windows facts (bin over cap silently deletes permanently; cwd inside folder blocks) - machine notes, not framework. |
| 11 | Fresh-clone gate skips ~180 local-data tests | PARTIAL | fan-out.md worktrees: "Gitignored inputs ... are absent in a worktree: ... expect skipped tests and say which in the report"; gate.md: "a skip that grew ... is a regression"; gate.md line 51: "the id does not cover gitignored files". Missing: a green fresh-clone/CI gate does not run those tests, so the skipped count must be reported and the main-tree run is a separate push step. No open task. |

## Proposed tasks
1. Long-running jobs rule (items 7, 8 lesson): launch detached as one script, never background an && chain, stop by process group and verify with ps, pin tools by path/version and record which one ran. File: kit/docs/runbooks/fan-out.md (new "Long jobs" under Watchers), mirrored to docs/runbooks/fan-out.md byte-equal; FRAMEWORK §6.6. Link CE-110.
2. Workflow agents are not messaged (item 3): never SendMessage a running workflow agent; hand it input through a scratch file, or let it finish. File: kit/docs/runbooks/fan-out.md Workflows (+ copy).
3. Fold into CE-214 (item 9, 10): add the four sweep classes already listed, plus "deletes are recoverable (trash/recycle, not rm), done by the session". File: kit/docs/runbooks/fan-out.md.
4. Skipped tests in a clean checkout (item 11): report skipped count and why with every fresh-clone/CI green; local-data tests need a main-tree run before push. File: kit/docs/runbooks/gate.md "Running it" (+ copy); repo values go in the adopting repo's CLAUDE.md Gate.
5. Multi-line text goes through a file (item 5): commit messages and owner words via `-F`/Write tool, and write for the shell you chose. File: kit/docs/runbooks/manual-mode.md § context-engine commit or fan-out.md; or contract.md Environment.
