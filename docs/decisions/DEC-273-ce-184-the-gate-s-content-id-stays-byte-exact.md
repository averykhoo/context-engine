---
type: Decision
id: DEC-273
title: "CE-184: the gate's content id stays byte-exact (no CRLF normalisation in gate.py::_fingerprint): a false red is preferred over a false green, and a new id algorithm would stale every recorded row"
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:7530af5f81c56274d689f2d88523c9d14cdc77a3d72639bbddc4d97d6f904ab1
---

The gate's content id stays byte-exact: no CRLF normalisation in `gate.py::_fingerprint`. A CRLF checkout then gives a false red (a green run stales with no content change), never a false green: a byte-sensitive test can pass on LF bytes and fail on CRLF ones, so an id that treats them as equal would carry a green row onto a tree it never ran on, against "it fails loudly, never plausibly". A new id algorithm would also need a `g2` id that stales every recorded row. A `gate status` hint naming the line-ending cause is out of scope here, a possible follow-up.
