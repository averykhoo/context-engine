# CI divergence: green on Windows, red on CI's Linux runner, 2026-10-13 (CE-67, US-18)

FROZEN 2026-10-13d. What made three tests pass on the owner's machine and fail on CI, how each was
reproduced on the owner's machine, and how to avoid the class. The tool is `tools/linux_gate.py`;
the guards are `tests/test_portability.py` and `tests/test_ci.py`.

**What happened.** Commit `39e09ca` passed the gate locally (Windows 11, Git for Windows 2.45.1,
Python 3.12: `626 passed`) and was pushed; CI's run 38417074413 (`ubuntu-latest`, git 2.55.0,
Python 3.12) reported `3 failed, 623 passed`, all three in `tests/test_commit.py` (new in CE-55).

**Reproduced locally.** `tools/linux_gate.py 39e09ca` (Docker Engine in WSL2) gave `3 failed,
623 passed`, the same three tests, once the container was shaped like the runner. Getting there
took three steps, and each step's misses are themselves findings:

| image | git | result on `39e09ca` | what it showed |
|---|---|---|---|
| `python:3.12-slim` + Debian's git | 2.47 | `2 failed` | two failures come from Linux itself |
| `ubuntu:24.04` + git-core PPA | 2.55.0 (CI's) | `2 failed` | the third is not a git-version difference |
| the same + `/etc/gitconfig` `safe.directory = *` | 2.55.0 | `3 failed` (CI's three) | the third comes from the runner image's system git config |

## The three footguns

1. **Patching `time.sleep` on the module patches it for the standard library.**
   `test_a_held_index_lock_is_waited_for` did `monkeypatch.setattr(C.time, "sleep", stub)`, where
   `C.time` is the `time` module itself, and the stub deleted `index.lock`. On POSIX,
   `subprocess.run(..., timeout=)` waits for the child by polling with `time.sleep` (CI's recorded
   waits: `0.001, 0.002, 0.004, ...`, doubling, not the engine's `0.05` steps), so the stub deleted
   git's own live lock mid-write: `fatal: unable to write new index file`. Windows waits on a
   process handle and never calls `sleep`, so it passed there.
   *Avoid:* patch the module's own name for the dependency (`setattr(C, "time", <stand-in>)`), never
   an attribute of a standard-library module. Guarded by
   `test_portability.py::test_no_test_patches_an_attribute_of_a_standard_library_module`.

2. **GitHub's Ubuntu runner trusts every directory.** The runner image's `install-git.sh`
   (actions/runner-images, `images/ubuntu/scripts/build/install-git.sh`) appends
   `[safe] directory = *` to `/etc/gitconfig`, a workaround for actions/checkout#760. So git on CI
   never refuses a repository for "dubious ownership", and `test_a_repo_git_refuses_says_so`, which
   fakes that refusal with `GIT_TEST_ASSUME_DIFFERENT_OWNER=1`, saw the commit succeed. Git for
   Windows' own system config differs the other way (`core.autocrlf=true`).
   *Avoid:* tests read no machine git config: `tests/conftest.py::_no_machine_git_config` sets
   `GIT_CONFIG_NOSYSTEM=1` and points `GIT_CONFIG_GLOBAL` at an empty file for every test and every
   process it starts. Guarded by `test_portability.py::test_git_in_a_test_reads_no_system_or_global_config`.

3. **Text-mode stdin on Windows sends `\r\n`.** The test helper `test_commit.py::trailers` fed a
   commit message to `git interpret-trailers --parse` with `text=True`; on Windows Python turns
   each `\n` into `\r\n`, and git then does not unfold a trailer's continuation line
   (`['Closes: CE-1', ' continued', ...]`). On Linux git unfolds it, as `--parse` documents
   (`['Closes: CE-1 continued', ...]`). The test's expected value had been written from the Windows
   output. *Avoid:* send bytes to git (`input=msg.encode("utf-8")`), and write an expected value
   from the documented behaviour, not from one machine's output.

## Avoiding the class

- **Run CI's job locally before a push:** `<interpreter> tools/linux_gate.py` (CLAUDE.md § Gate).
  The commit need not be pushed; the image is built once and cached. `test_ci.py::
  test_the_local_linux_gate_runs_the_workflow_s_steps_on_its_runner_s_shape` keeps it in step with
  the workflow.
- **When CI and the local Linux gate still disagree,** compare the versions the tool prints with
  the CI log's (`git version` in the checkout step) and the runner image's own install scripts
  (actions/runner-images): CI's git moves with the git-core PPA, and `ubuntu-latest` moves to new
  Ubuntu releases (`linux_gate.RUNNER`).

Sabotage: `tools/sabotage_ce67.py`, every row red on 2026-10-13d; the tool itself is red on
`39e09ca` (above) and green on the fix.
