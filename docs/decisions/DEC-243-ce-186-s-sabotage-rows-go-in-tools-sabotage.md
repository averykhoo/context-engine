---
type: Decision
id: DEC-243
title: CE-186's sabotage rows go in tools/sabotage_ce185.py, not a new script
actor: claude-code/claude-sonnet-5-5
decision_status: PROVISIONAL
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:95cb0b1464ada1f1ef75b6eca4813aa9282458b00fe6881f2c187bc6bb6446e3
---

CE-186 sabotage rows (enum order, escaping before and after a link) are appended to tools/sabotage_ce185.py, the site table, rather than a new sabotage_ce186.py that would duplicate its runner.
