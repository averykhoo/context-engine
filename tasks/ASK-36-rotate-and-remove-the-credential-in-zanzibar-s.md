---
type: Question
id: ASK-36
title: Rotate and remove the credential in zanzibar's local Claude settings?
brief: 'Owner-only: outside the repo; never printed or copied'
pri: LATER
state: open
deps: []
source: session 2026-11-03b
created: 2026-11-04
moved: 2026-11-03b
updated: 2026-11-04a
last_asked: 2026-11-03b
---

## Context

The CE-167 survey found a credential stored in plain text, together with a broad push permission, in
zanzibar's main checkout's gitignored local Claude settings file. Nothing was printed, copied or changed, and
the file was left out of the backup on purpose.

## Options

- The owner rotates the credential and removes it, and the push permission, from that file.
- Leave it as is.

## Recommendation

Rotate and remove: a plain-text credential in a settings file gets copied by tools that do not know it is there.

## Log

- 2026-11-04a (claude-code/claude-opus-5-5): Owner, 2026-11-04a: "36 - what's this credit for? Push permission is fine as long as it doesn't publish". Answered in chat 2026-11-04a: the credential is a GitLab personal access token saved inside six allow rules (an export of GITLAB_TOKEN and five curl lookups of GitLab users and csitsg group members), left by earlier always-allow clicks; zanzibar's remote is GitHub and needs none of it. Bash(git push:*) also allows a tag push, which publishes. Still open: remove the six entries (and rotate?), and add deny rules for tag pushes?
