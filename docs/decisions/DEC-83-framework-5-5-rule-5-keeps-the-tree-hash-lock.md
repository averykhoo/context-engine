---
type: Decision
id: DEC-83
title: FRAMEWORK 5.5 rule 5 keeps the tree-hash lock standard; the per-repo lock is a deviation filed as CE-135
decision_status: PROVISIONAL
actor: claude-code/claude-opus-5-5
decided: 2026-10-24
session: 2026-10-23f
body_sha: sha256:4c89d1cd3326bdbfc3ea5acf53e08105660f93180e66d5679122c42b5b09c921
tasks: [CE-93]
---

An agent's call under P8 (cheap to undo), made by CE-93's builder in session 2026-10-23f and landed in c5b812f. Recorded afterwards from the builder's report (its PROVISIONAL call P-9). Not owner words.

**Call.** FRAMEWORK §5.5 rule 5 keeps the old standard, minus its status marker: background agents, gates and engine writes use locks (G-V3) keyed on the tree hash. The engine's actual per-repo write lock, with no gate or agent lock, is stated as a deviation in `docs/engine.md` § The engine lock and filed on the board as CE-135, whose part 2 offers the owner the ruling on a per-repo lock standard.

**Why.** Restating rule 5 as the per-repo lock the engine has would change a rule, which this rewrite does not do (verify-1's blocker B2), and the choice of lock standard is the owner's. Restoring the old standard keeps the spec unchanged and puts the gap where it will be worked.

Task: CE-93. Commit: c5b812f.
