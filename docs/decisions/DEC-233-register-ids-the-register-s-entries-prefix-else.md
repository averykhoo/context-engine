---
type: Decision
id: DEC-233
title: "Register ids: the register's entries' prefix, else the last logged register.append id's, else RISK; mixed prefixes refuse filing; numbers continue across prefixes; no config key"
actor: claude-code/claude-opus-5-5
decision_status: PROVISIONAL
tasks: [CE-56]
decided: 2026-11-08
session: 2026-11-07e
body_sha: sha256:d0ddc7325be2c28e31e926490aea7ae83b51f2aa324472ce027ddb67bb607d22
---

For CE-56: DEC-38 makes RISK the standard prefix of residual-risk register entries, but review.py and working.py hard-code INV, and this repo's register keeps INV (DEC-162).

The call: the register's next id takes the prefix its entries use; with no entries, the prefix of the last id the op log's `register.append` lines name; with neither, RISK. Numbers continue across prefixes (the highest number of any entry or logged id). A register whose entries use two prefixes refuses filing until they are renamed to one by hand, and an entry reusing another's number under a different prefix is a problem. No config key: the register already says which prefix it uses, as the criteria file does (working.py::Engine._next_criterion).

Options:
(a) the register's own prefix, else the logged one, else RISK: chosen;
(b) a config key: rejected, a dataclass default would silently switch an adopted repo from INV to RISK on upgrade;
(c) always RISK: rejected, this repo keeps INV.

Cost to undo: cheap (review.py's series and its tests).
