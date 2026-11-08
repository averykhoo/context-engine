---
type: Decision
id: DEC-270
title: 'CE-184: init warns where the checkout converts line endings and writes no git config or eol attribute: DEC-94 stands; the remedy is the per-clone fix in the kit README, which the owner applies'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:1a39471076d8e7751c654d7b4dc1cde1d0606eee12d91763a5f3b56348dd1ed5
---

init warns where the checkout converts line endings (`core.autocrlf=true` with `context.toml` not pinned `eol=lf`), and writes no git config and no eol attribute. DEC-94 stands: an eol attribute renormalises the owner's whole tree, and a clone's git config is per clone and the owner's. The remedy is the per-clone fix the kit README § 2a names, which the owner applies: `git config core.autocrlf input`, then once `git rm -r --cached -q . && git reset -q --hard`, or a clone made with `git clone -c core.autocrlf=input <url>`.

Rejected: init running `git config` itself (outside what init owns, and it still cannot rewrite files already CRLF without `rm --cached` plus `reset --hard`, which is destructive in a shared tree); init writing `* text=auto eol=lf` (DEC-94).
