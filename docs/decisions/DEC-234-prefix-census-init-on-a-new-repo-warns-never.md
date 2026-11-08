---
type: Decision
id: DEC-234
title: 'Prefix census: init on a new repo warns, never refuses, where a kind prefix already appears in tracked files (git ls-files; no git, no census)'
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:45b6dde0d9aa2d9cec52ec4b7b5687b68c222c97c75efe554083a039c2e20a6d
---

For CE-56 (from CE-167): zanzibar's audit labels D7 and S-1..S-7 collided with the kit's default prefixes, and `init --dry-run` gave no warning.

The call: `init` on a repo with no `context.toml` counts, per kind prefix, the `<PREFIX>-n` and `<PREFIX>n` hits in the files git tracks (`git ls-files`), skipping files over 1 MB and binary ones, and warns once per prefix with hits, naming the count and the first hit. It never refuses. Not a git repo, or no git: no census. A re-run on an existing config: no census.

Options:
(a) warn on tracked files at a fresh init: chosen;
(b) refuse: rejected, a hit may be this kind's own ids from before;
(c) walk the whole tree: rejected, it reads build output and untracked files the owner never cited.

Cost to undo: cheap (one function and its test).
