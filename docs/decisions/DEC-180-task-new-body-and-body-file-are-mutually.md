---
type: Decision
id: DEC-180
title: 'task new: --body and --body-file are mutually exclusive'
actor: claude-code/claude-sonnet-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:a70852eb991af0e1bf43dca83c6aa30b7804059a25a946f160de12393c0a543e
---

task new takes --body and --body-file as a mutually exclusive pair, as ask new and task close do: giving both is an argparse usage error (exit 2, nothing written), not one silently winning, which would lose the other's text.
