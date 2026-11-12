---
type: Decision
id: DEC-338
title: "The README is for readers: no record ids or progress tracking; fix muse's CE-231/CE-232 records and the headroom follow-ups, then gate and push"
actor: owner
decided: 2026-11-12
session: 2026-11-12b
decision_status: ACCEPTED
body_sha: sha256:7161d9b27cd5401ddf541d9f66eb43d4c670de0fe385202ba8ce1eda6b0c4e47
---

"Hold on why is readme citing tasks? Isn't readme supposed to be really just something useful to read? And the job log and board are handled by the tool?"

"Yes that can be a standing rule, esp since readme is the default page shown to people on github, so it should be actually useful to read, and should orientate the reader to find what they need, or straight up have what they need.

Also fix the muse stuff including  the full suggested fix

Then gate and push as usual"

(Answering session 2026-11-12b's review of bc9f1c3 and 63db00b, two commits by muse, an agent that cannot run the engine. The rule it proposed: the README is for readers, so it carries no record ids and no progress or status tracking, which live on the board; a lint check fails a record id in the README. "The muse stuff" is that review's list: CE-231, CE-232 and AC-208 were written by hand with no op lines, the two tasks are still open though their logs say closed, AC-208 went straight to tested, the commits carry no `Session:` trailer, and the sabotage line is in a task log, not a commit. "The full suggested fix" is the review's optional part too: the headroom warning's remedy names where cut text goes, headroom respects `[guards] off`, and its percentage no longer rounds 9,996 of 10,000 bytes up to 100%.)
