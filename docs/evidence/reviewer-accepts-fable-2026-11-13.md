FROZEN: evidence, session 2026-11-13c. A copy of .scratch/fable-review/fable.md, made for the owner's question of a reviewer model accepting provisional decisions; not yet a decision.

# Fable's opinion: a reviewer model accepts provisional decisions

claude-fable-5-1, 2026-11-13, read-only. Sources: brief.md, census.md, US-24, FRAMEWORK P8 and §6.5, charter goals, `context.toml` [kinds.decision].

## 1. Opinion

**Yes, with two corrections and one worry the proposal does not name.** The data is clear: of 243 agent decisions the owner changed 4 (1.6%), one of substance (DEC-107), and that one came through fable, not the owner. The owner has accepted in two bulk "take fable's recs" ops and nothing else; PROVISIONAL has stopped carrying information (180 unread). A fable pass that turns PROVISIONAL into a real status is cheaper than the status quo and loses nothing the owner was supplying. US-24 and DEC-48 already say this in the owner's words.

Where I differ from the coordinator:
- **"Escalate when it quotes or interprets owner words" is too wide.** Citing owner words is what a good decision does (DEC-217..223 all do; 15 of 243 are "interpretation", 1 changed). The real trigger is *changing what an owner record requires*: a `supersedes`, `relaxes`, `narrowed_by` or `amends` link to an owner-actor record. That is mechanical; "interprets" is not.
- **A cap of ~3 unreviewed provisional decisions stops every build.** One task yields 5-12 (CE-126: DEC-274..282). Cap the *owner escalations* waiting, not the decisions; fable's own queue drains at each task close.
- **Independence**: fable needs the decision text (its why is the record), the records it cites and the diff. Withhold the maker's verdict and chat, not its record.

The worry: **fable shares the maker's priors.** The owner's 30 corrections cluster on process weight and over-engineering (7: DEC-36 "do we really need to commit at every write?", #11, #12, #16, #24), reading rules too narrowly (#1, #3), and taste (DEC-27/38, #9, #18). None is a code-level call. A reviewer trained like the maker endorses the same weight (DEC-337: nine of nine ENDORSE), so this workflow removes the only *external* signal where the agents are weakest. The list below is built around that: silent acceptance is confined to the category the owner has never corrected (implementation detail under a criterion), and anything that adds surface, cost or a name gets a digest line the owner can skim in seconds. Two more risks worth naming: ACCEPTED must stop meaning "the owner agreed", or later agents will cite fable-accepted decisions as owner intent (the body_sha machinery exists exactly to keep that provenance clean), hence `accepted_by`; and nonstop running stacks decisions on unreviewed ones, so the owner's look happens per close, not per week, and an open escalation blocks the items that depend on it, never the session.

Compaction itself I agree with the coordinator on: state is in records, orient re-fires; clear at task boundaries. The session should pick from NOW only, promote from NEXT only by the rerank procedure (DEC-64: rerank only when NEXT is empty), and stop when NEXT is empty rather than invent work.

## 2. Escalation list

Conditions read record fields and diff paths; "owner record" = a story, charter goal, or a DEC with actor `owner`/`owner asked` that stands. First match from the top wins.

**ASK THE OWNER** (blocks that item and its dependents; work continues elsewhere)
- A1. The decision links (`supersedes`, `relaxes`, `narrowed_by`, `amends`) to an owner record, or its text contradicts a sentence it quotes. Why: this is the one place agents read rules too narrowly (#3 DEC-44/60; #4 DEC-22). 
- A2. The diff touches `docs/charter.md`, a story's status, or sets a task to NOW outside the rerank. Why: goals and priorities are the owner's (P8; #1, DEC-6, #14).
- A3. Not cheap to undo per P8: push, tag, release, deleting untracked files, any path outside this repo (another repo, global `CLAUDE.md`, `~/.claude.json`). Why: the owner's by rule; adoption placement is 7 of 30 corrections (#10-14, #21, DEC-1).
- A4. The diff touches `kit/contract.md`, `CLAUDE.md` § Gate or § Rules, FRAMEWORK §1 principles or §6.5, `[gate]` in `context.toml`, or this list. Why: the rules that decide who decides are not self-amended.
- A5. After one review round-trip fable and the maker still differ, or fable's verdict is anything but ENDORSE. Why: "not sure" defined as a disagreement on record, not self-reported confidence.
- A6. GAP: fable cannot name a covering record (§3), or the covering story is one of the thin ones (US-12, 13, 16, 18, 20, 21, 22). Why: nothing to derive from; the ASK is phrased as "amend US-n", so one answer covers the next ten decisions.
- A7. Adds a recurring per-session or per-commit cost: an orient part, a hook, a commit milestone, a gate step. Why: the owner's most repeated correction (#8, #11, #15 DEC-64, #16).

**FABLE ACCEPTS AND FLAGS** (one digest line: id, title, why flagged)
- F1. Adds a new guard id, operation, record kind or field, CLI flag, config key, or procedure step. Why: surface growth is where over-engineering shows (DEC-36, #16, #24). A clause added to an existing guard (DEC-102, DEC-112) is C3, not this.
- F2. A user-visible name: id prefix, flag, config key, FRAMEWORK term. Why: taste cannot be derived (DEC-27/38, #9 DEC-39, #18 DEC-338).
- F3. Any path under `src/context_engine/kit/` or a default an adopting repo inherits. Why: the one substantive flip was a kit default (DEC-107).
- F4. `refs` names an owner record but no criterion: it interprets rather than implements. Why: 6.7% change rate, highest of the categories.
- F5. Drops, splits or defers part of a task whose body holds owner words (DEC-138, 198, 213, 315). Why: scope is the owner's to narrow.
- F6. Fable accepted after a change the maker made on request. Why: a disagreement happened, even if resolved.
- F7. `refs` names a decision fable accepted in the same session. Why: stacking; the owner sees the chain's root.

**FABLE ACCEPTS** (silent; `accepted_by` set, a random sample surfaces in the digest)
- C1. Implementation detail in `src/` or `tests/` with a criterion in `refs`/`tasks`, gate green, no new surface. Evidence: 89 such decisions, 2 changed, both really F3/A7 cases.
- C2. Refusal wording, remedy text, error placement, fixtures, internal symbol names.
- C3. Which existing guard or section a clause belongs to; a sabotage row's script; a dated evidence doc's name.
- C4. A decision that applies verbatim a criterion, procedure step or owner sentence it quotes.
- C5. Agent self-supersession that fixes the agent's own earlier call (DEC-88/125, DEC-91/92).

## 3. How the lines move with maturity

**Covered, mechanically:** a decision is COVERED when its `refs` (or `Derived from:`) names a record R that is a live owner story, a standing owner DEC, or a charter goal, **and** fable's review note quotes one sentence of R that decides the call. This is the test `ask decide` already imposes on its `sources`; reuse it. No quotable sentence means GAP, whatever the refs say. Cheap-to-undo GAPs (P8) are F-tier; the rest A6. Citing is not covering: DEC-6 cited the owner's trial order and was still reversed, because the cited words did not decide the point.

**Thin areas:** US-22 (unspecified), US-12 ("just be a task"), US-13 (git fit unknown): no decision under them is accepted by fable at all; the first task there opens with one batched ASK whose answer is an amendment, then decisions can be covered by it. US-16, 18, 20, 21 (one or two sentences): first decision under each is A6, later ones F4 against the amendment. Goals with few stories (G-2: 2) are not thin by themselves; a goal row's "Measured by" sentence counts as covering text.

**Over time:** every owner answer lands as a story amendment or owner DEC, so the covered set grows and the A6 rate falls without changing the list. The list itself moves on measured override rate, by tier: after 50 fable acceptances with the owner overturning none of the sampled C-tier ones, F1 and F4 drop to C; any overturned silent accept moves its condition up one tier for the next 50; a direction-changing reversal (the kind of #1, charter scope) resets all counts. The list is an owner DEC, so each move is a dated amendment, and the rate is computable from `accepted_by` against later owner `supersedes`.

## 4. The 180 unreviewed PROVISIONAL decisions

Do not ask the owner to read them, and do not have fable read them one by one in chat. They are CE-build design calls, mostly DEC-179..323, grouped by task, already built and verified, and the owner has run the engine on top of them for a week. One fable pass, batched by task, applying §2 retroactively: C and F tiers accepted with `accepted_by: claude-fable-5-1`, F titles listed to the owner in one message, A-tier ones (by title I expect under 15: DEC-73..77 delegated-ruling provenance, DEC-244..246 HOLD tier, DEC-307..309 P19, DEC-317..321 global CLAUDE.md, DEC-322) raised as a handful of ASKs grouped by topic, not per decision. This pass is also the calibration sample: the owner spot-checks ten random C-tier accepts from it, and the result sets the starting thresholds in §3. Where a task is closed and verified, BUILT would be the honest status over ACCEPTED, since it claims a fact, not agreement; worth deciding before the pass.

## 5. What the engine needs (minimal)

1. `accepted_by: <actor>` on the decision, written by `decision accept` from the caller's actor; lint reds a post-cutover ACCEPTED decision without it. Without this, ACCEPTED silently becomes "owner agreed". Also `review: accept|flag` beside it, so the digest and the override rate can be computed by tier.
2. `decision accept` by a non-owner requires `--covered-by <id>` naming a live owner record, or `--gap`; refused otherwise, and refused when the decision's `refs` names an open ASK (the stacking guard). Sabotage both.
3. No new kind for escalations: an A-tier item is an ASK with the decision in `refs` and fable's recommendation as part one; orient already lists open questions, so stop condition (b) is "an open ASK references a PROVISIONAL decision".
4. `session close` digest: the F-tier lines, plus two C-tier accepts chosen by a hash of the session key (reproducible). Format only.
5. A `decision find --accepted-by <actor>` filter, so the §3 rate is one query. Nothing else; the batch rule (one fable call per task close, never fanned out, DEC-18) is procedure text, not code.
