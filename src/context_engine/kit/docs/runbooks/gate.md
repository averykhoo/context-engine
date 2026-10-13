---
type: Runbook
title: "Gate: running it so its result can be trusted, and the test baselines"
source: FRAMEWORK §7.5, §6.3, §6.8, P5, P15
created: 2026-10-13
mode: replaced
liveness: LIVING
---

# Gate

The gate is the one command whose result says the tree may be committed or pushed. What it is
and when it runs are the framework contract's § Gate; where it sits in each ritual is
[rituals.md](rituals.md). This file is how to run it so that its result is true. The repo's
values (its test command, its interpreter, its CI workflow file, its suites) are in its
`CLAUDE.md` § Gate, never here. A red CI run is a red gate; without CI, do CI's run by hand
([rituals.md § Push and CI](rituals.md#push-and-ci-68)).

## Running it

| Do | Why |
|---|---|
| Capture the exit code itself: `<gate> > <log> 2>&1; rc=$?`, then branch on `rc` and read the result line | piped through `tail` or `tee`, a command reports the pipe's status: a red gate reads as exit 0, and a following `&&` runs on |
| Re-measure every time; never work a count out from a recorded one | a carried-forward number stops being true without anyone noticing (P5) |
| In a second worktree, make the gate import that worktree's code, not the main checkout's (a Python editable install points at the main tree; with a `src/` layout, set `PYTHONPATH=<worktree>/src`) | otherwise the gate tests the main tree's code and passes for the worktree |
| Check a worktree out with the line endings the repo's byte checks expect (git: `-c core.autocrlf=false` on every command that checks files out) | a checkout that converts line endings fails byte-equality checks for no real reason, or hides a real difference |
| Where CI runs on another platform than this machine, run CI's job on that platform here before a push: a container shaped like CI's runner (its OS release, its git and that git's system config, its Python), on a fresh clone of the commit; the repo's `CLAUDE.md` § Gate names the command | a gate green on one platform can be red on another (a test that leans on the standard library's platform internals, the machine's git config or text-mode line endings), and the push is where it shows |
| Red: say what is red and leave it. Never commit to make progress look like assurance | a commit on red is a false resume point for the next session |
| A red you did not cause is reported, not fixed silently or buried under yours | the next reader must be able to tell whose red it is ([rituals.md § Clean close](rituals.md#clean-close-63), item 1) |
| Record the result verbatim in the close's `guards:` receipt ([rituals.md § Clean close](rituals.md#clean-close-63), item 2), naming the commit it ran on where you can | "tests passed" is worth recording only with what it passed on (P15) |

## Test baselines

One dated baseline per suite (P5): its pass count, and its time where that matters, with when it
was measured.

- **Where it lives.** For the gate's own suite, the baseline is the `guards:` receipt of the
  newest `kind: close` entry in the ledger, dated by that entry's session key; a pause or open
  entry carries none. A suite outside the gate (a slow, performance or numerical suite) keeps one
  dated line where the repo's `CLAUDE.md` § Gate names it; a new measurement replaces the line,
  and git keeps the old one.
- **Compare every run with its baseline.** Fewer passing tests, a test that vanished, a skip that
  grew or a time that jumped is a drop.
- **An unexplained drop is a blocker.** Do not commit over it. An explained one (a test removed on
  purpose, a suite split) says why in the commit message and the close summary.
- **A numerical or performance check** moves only within its declared tolerance against a frozen
  baseline (FRAMEWORK §3.3); the tolerance is the repo's, in its criteria.
