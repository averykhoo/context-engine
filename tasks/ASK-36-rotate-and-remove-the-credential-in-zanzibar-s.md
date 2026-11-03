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
updated: 2026-11-03b
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
