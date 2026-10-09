---
type: Decision
id: DEC-21
title: 'Section 12.3 answers: Q-F, Q-G, Q-H defaults accepted; Q-J deferred; no housekeeping write budget by default (Q-K)'
actor: owner
decision_status: PROVISIONAL
answers: Q-F, Q-G, Q-H, Q-J, Q-K
decided: 2026-10-09
session: 2026-10-09e
body_sha: sha256:78b9391943bfaa8b398fffcb2415db27e9d439be31e806fbfae96cb1863a1c24
---

The owner, 2026-10-09 (session 2026-10-09e), answering FRAMEWORK §12.3:

> in 12.3 in framework.md
>
> okay to q-f, q-g, q-h, q-i is already settled
>
> q-j: i think it would be helpful that the engine has a way to generate it if asked, and a human-answered (i.e., edited in place with answers) file can then be manually read back and filed against the open questions that were answered. but maybe this can be a future thing, we have no need of this for now, we'll default to claude rc
>
> i'm not sure we need a budget - measure the token counts etc, but i think sending off an editor agent might be cheap enough that we don't need a change budget? and i'm not confident that sessions have consistent sized changes, so a reasonable budget might actually be unreasonably large. but i guess if an unreasonably large budget is worth more than no budget we can still do that, but if i hit the budget i'm probably just going to say nvm write anyway and increase the budget

So:
- **Q-F, Q-G, Q-H: the stated defaults are accepted.** One owner per repo, named in the charter; other humans' stories under their own id; conflicts go to the owner. Only remote-control humans are nagged in chat; questions for anyone else stay as board rows. The ledger stays one file under the engine lock (already DEC-14).
- **Q-I** was already answered (2026-10-08).
- **Q-J: deferred, not refused.** The owner read it as a generated file of open questions: the engine generates it on request, a human answers in place, and the answers are read back and filed against the questions they answer. Not needed now; the channel stays Claude remote control.
- **Q-K, the last paragraph (no question letter given; read as Q-K):** no housekeeping write budget by default. Measure token counts and similar instead. An editor agent may be cheap enough not to need one, and session change sizes vary, so a sensible budget may be unreasonably large. A budget may still be set if it is worth more than none, but hitting it would most likely be overridden ("write anyway") and the budget raised. The stale-stub window (G-W11) was not addressed and stays open.
