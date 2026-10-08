---
type: Decision
id: DEC-14
title: 'CE-2 working-state calls: one-file ledger, baton and pause kinds, orient cap 6000 B'
actor: agent (claude-opus-5-5)
decided: 2026-10-08
session: 2026-10-08d
decision_status: BUILT
tags: [working-state, engine]
answers: Q-H
body_sha: sha256:df72a86affc18881ed314835f62137fe877fdcfd098c98f96e336d11f2d9606d
---

CE-2 built the working state. These are the agent's calls it required; push back on any.

1. **Q-H: the ledger stays one file under the engine lock** (FRAMEWORK §7.1, §12.3), not one
   file per entry. Every reader already cites `docs/ledger/session-log.md`; the lock already
   serialises writers, and `session.start` proved the insert surgical (the first engine-minted
   stub, 2026-10-08d, changed six lines and nothing else). Rotation by period stays unbuilt.
2. **Batons and pauses are record kinds `baton` (`BTN-n`) and `pause` (`PAU-n`)** in
   `docs/working/`, mode `stamped`, with `state: open | done | expired`. New id prefixes, so
   they collide with none of DEC-7's (checked 2026-10-08d).
3. **"Older than two sessions" (G-W3) means two `close` or `pause` ledger entries keyed after
   the owning session.** A baton from 08d survives 08e and 08f; at 08g's start it is expired.
   Housekeeping (`ce baton expire`, actor `process:housekeep`) files it as a LATER task.
4. **`orient()` is capped at 6000 bytes** (`orient_max_bytes`). Provenance: `ce orient` on this
   repo measured 3015 bytes on 2026-10-08d (banner 1.1 KB, three NEXT rows, CE-2's Traps and
   Read first; no batons, questions or other sessions). 6000 is about twice that: room for
   two more NEXT rows, roughly ten baton or pause lines and a few questions. Over the cap every
   heading still prints and a cut section names where the rest is.
5. **G-W11's stale-stub window is not set here.** Marking a dead stub `abandoned` is
   housekeeping (CE-6), and the window needs measured session lengths (G-D9); CE-6 owns both.
6. **Fields declare types in `context.toml`** (`types = { created = "date", ... }`): CLI strings
   are coerced by them and writes of the wrong type are refused, which closes the quoted-date
   trap seen 2026-10-08c.
7. **Engine-owned board keys** (`state`, `status`, `closed`, `moved`, `updated`, `pri`,
   `deps`, `last_asked`) change only through their operation; generic `set` refuses them and
   names the operation (G-W7's write-time half).

## Amendments
