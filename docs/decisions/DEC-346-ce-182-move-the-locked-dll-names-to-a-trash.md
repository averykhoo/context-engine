---
type: Decision
id: DEC-346
title: 'CE-182: move the locked DLL names to a trash folder that a logon RunOnce deletes'
actor: owner asked
ruled_by: claude-code/claude-opus-5-5
decided: 2026-11-14
session: 2026-11-14c
decision_status: PROVISIONAL
body_sha: sha256:9a1ad6e3288e9981e9c8872ad2d06d7238977d4cb221f2754142a70f31419890
---

Owner, 2026-11-14c, after the coordinator offered two ways to clear CE-182's 35 locked DLL names (queue a delete at next boot with an admin prompt, or move the names into a trash folder now and empty it once no conda Python runs): *"Okay I'll let you decide how to clean up"*

## Ruling

Move the 35 names into C:\Users\user\.dll-trash now (Windows allows renaming a loaded DLL; tested on ffi.dll first), delete the then-empty ce11-rehearsal and ce167-rehearsal folders, and register one per-user RunOnce entry (HKCU, no admin) that deletes C:\Users\user\.dll-trash at the next logon, before most programs start. If something has a DLL loaded by then, the folder stays and is harmless: 0 bytes of its own, every name a hardlink the live envs share. Not the boot-time delete: it needs an admin prompt the agent cannot answer. CE-182 then holds only the zanzibar backup.
