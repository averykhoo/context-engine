---
type: Decision
id: DEC-294
title: 'CE-175 graft scope: the graft applies only when every uncommitted op line naming the note is banner.set, HEAD has the note and the working note has a banner; otherwise the whole file, as before'
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:3850d8bb32a21bceb910ee9a6e77b77a55431655a82c367157fd4fafb4737971
---

The banner-only graft (CE-175) applies only when all of these hold: the note is configured
(`[working] handoff`), the commit carries it and it was not given by path; every uncommitted op line
the commit takes that names it is `banner.set`; HEAD has the note; the working note has a banner;
and the grafted note differs from the working note once CRLF is normalised to LF. Otherwise the whole
file goes, as before. So a commit with no hand edit, or one that adds the note to git for the first
time, behaves as it did, and an op that writes the note in other ways is never cut short.
