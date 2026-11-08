---
type: Decision
id: DEC-271
title: 'CE-184: the line-ending fix the kit names is core.autocrlf=input, not false: under input a CRLF working file hashes as its LF blob and a commit normalises it, while false shows phantom modifications and can commit CRLF'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:2d5c56a392a0593381f20430d3545fba3e399d290612854bc5df650b48f31d25
---

The line-ending fix the kit names is `core.autocrlf=input`, not `false`. Under `input` git converts nothing on checkout and converts CRLF to LF on add, so a CRLF working file hashes as its LF blob (no phantom modification) and a commit normalises it. Under `false` a CRLF working file left from an earlier checkout shows as modified and can be committed CRLF.
