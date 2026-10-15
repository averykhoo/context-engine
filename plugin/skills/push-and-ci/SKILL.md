---
name: push-and-ci
description: Use in a repo run by context-engine (context.toml at its root) before any git push, tag push or pull request, and whenever the owner asks to push or release. Push and CI (FRAMEWORK §6.8) - the owner's permission, the gate green on exactly that commit, a background CI watcher keyed on the pushed hash, the verdict reported; a release also follows release.md.
---

# Push and CI

Runbook: `docs/runbooks/procedures.md` § Push and CI

Open that section of this repo's own copy now and do its rows in order: it is the source, and its
"By hand" column is the fallback when the engine errs. This skill only points there and quotes it, so it never
disagrees with the runbook the repo is pinned to. `context-engine` means the engine command the
repo's contract names (`<engine-python> -m context_engine`, with `CE_ACTOR` and `CE_SESSION` set).

What sessions miss here, word for word from the runbook (the engine's gate checks each line):
- Ask the owner; push only with permission. A push hold, if any, is a line at the top of the
  contract
- the watcher finds runs by hash, not "the latest run", which may be another session's
- It only watches: no fix, no re-run, no cancel, no push
- The push is not done until the watcher reports, and a red run is never described as done

If that section is missing, the repo's runbooks predate this plugin: read the runbook's headings
and use the one for FRAMEWORK §6.8.
