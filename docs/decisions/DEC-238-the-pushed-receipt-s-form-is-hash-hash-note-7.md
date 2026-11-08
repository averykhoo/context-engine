---
type: Decision
id: DEC-238
title: "The `pushed` receipt's form is `<hash>[, <hash>...]: <note>`: 7 to 40 hex chars each, each resolving to a commit in this repo, and a non-empty note; session close refuses anything else before its first write (CE-176)"
actor: claude-code/claude-opus-5-5
tasks: [CE-176]
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:d505c085ed3a1ae906fbfcbb11480a7d07c8985db779225801b743c537446e78
---

For CE-176: the `pushed:` close receipt clears orient's flag on a push made while no session was open, so a malformed one would either clear nothing or clear the wrong push.

The call: the receipt's form is `<hash>[, <hash>...]: <note>`. Each hash before the first colon is 7 to 40 hex characters and resolves to a commit in this repo (`git rev-parse --verify <hash>^{commit}`), and a non-empty note follows the colon (what was pushed, and whether the gate ran first). `working.py::Engine.session_close` refuses anything else before its first write, and stores the receipt with its whitespace collapsed.

Options:
(a) hashes only before the first colon: chosen;
(b) hex tokens anywhere in the receipt: rejected, English words of 7 or more hex letters ("defaced", "effaced") would be read as hashes;
(c) ranges `a..b`: rejected, the reflog names the tip, and a range adds parsing for no gain.

Not checked: that the note is true.

Cost to undo: cheap.
