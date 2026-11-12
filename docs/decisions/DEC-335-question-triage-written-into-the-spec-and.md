---
type: Decision
id: DEC-335
title: 'Question triage written into the spec and procedures: decision shape, arbiter as second opinion, interim for open questions'
actor: claude-code/claude-opus-5-5
decision_status: ACCEPTED
tasks: [CE-217]
refs: [US-24, DEC-325, DEC-18, DEC-310]
decided: 2026-11-11
session: 2026-11-11a
body_sha: sha256:f566cb72924d55ba987e06c353b2b5136c0f9c552731dd68cfd15ef9e395c896
---

**Decision:** the question triage of US-24 is written into FRAMEWORK §5.3 ("Triage before raising": derivable, cheap to undo, the rest), §6.2 item 4, §6.5, §6.6 Model choice and P8, and into procedures' Intake step 4 and Session start step 3, in this shape:

- A triage decision is the agent's own call: `actor: agent (<model-id>)`, PROVISIONAL, never `owner asked` and no `ruled_by`: a standing instruction to triage is not a delegation of the ruling.
- Its body holds the call, the why and a `Derived from: <ids>` line (`refs` lists them too); a derivable one ends in `## Second opinion`, led by `<model-id>, <date>, verbatim:`, quoting the arbiter whole, written at creation so `body_sha` covers it. The heading names no model, since FRAMEWORK and the kit name none and the arbiter's model varies by repo (audio-workspace's `## Fable's opinion (verbatim)` renamed).
- The second opinion is FRAMEWORK §6.6's existing arbiter role; no new role. One call per question, one question at a time.
- Until the operation that closes a question with an agent decision exists (CE-218), an open question found derivable gets the PROVISIONAL decision with `refs` naming it and a log line `decided by the agent as DEC-n (derivable; overturnable by an owner answer)`, and stays open until the owner answers (audio-workspace's practice before it had such an operation).
- The contract's Who-decides line is not changed now: a later task holds it for the next contract version bump (the DEC-310 precedent; G-D0 would turn red in every adopting repo).

**Why:** US-24 and DEC-325 ask for the triage; DEC-18 and its arbiter amendment bound the fable call; P8 already covers the cheap-to-undo half. The shape is the opus planner's for CE-217 (plan of 2026-11-10, addendum of 2026-11-11), followed by the builder.

**Rejected:** `actor: owner asked` with `ruled_by` (that shape needs delegating words quoted per answer, G-I3); keeping the opinion only in scratch (gitignored, P10); naming the op in this task's text (it does not exist until CE-218, and the runbook test refuses it).
