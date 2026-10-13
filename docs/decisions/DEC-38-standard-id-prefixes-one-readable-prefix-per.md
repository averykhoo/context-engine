---
type: Decision
id: DEC-38
title: 'Standard id prefixes: one readable prefix per record kind in every repo, 2 to 5 capitals; tasks take a per-repo prefix'
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-13
session: 2026-10-13c
body_sha: sha256:1a89871d2e88856250bb2a3b3df89bb50a3d27bf03cb1a32264ab25a140305dc
---

Owner, 2026-10-13c, right after answering ASK-5 (DEC-37):

"Also let's choose some convention for standardized prefixes for specific common categories, ASK is a good one, what else should we standardize?"

The agent proposed (2026-10-13c) that a prefix names a record kind, not a category of work (bug, spike and the like are `labels:` on tasks, since an item changes category and ids are never renumbered); one prefix per kind in every repo, set in the kit defaults; a per-repo task prefix; reserved prefixes for kinds not built yet. Owner:

"What's inv stand for? If we can use 2-5 chars in general what would be better prefixes? Fewer characters doesn't mean fewer tokens and it's less human readable so we might as well choose something easy to understand. Like Dec is fine for decision, ans or story are short enough, goal is also short enough. Exp and haz are fine

Help me come up with a list of conventional prefixes that we know for sure we need"

The agent's list (2026-10-13c): DEC (decision), STORY (story), AC (acceptance criterion), ASK (owner question), RISK (residual-risk register entry, was INV for "invariant", which the entries are not), GOAL (charter goal; frees G- for guard names such as G-D3), BATON (baton), PAUSE (pause); EXP (experiment or measured run) and HAZ (unverified hazard) reserved for kinds not built yet; tasks take a per-repo prefix of 2 to 5 capitals naming the board (CE here). Criteria were open. Owner:

"Hmm I'm okay with AC or ACC, ac is not as readable but I guess acc doesn't narrow it down by much and isn't a known term. DOD might work but I feel like that's less common? Any other ideas"

The agent weighed DOD (a Definition of Done is one checklist for every item, not a per-story criterion), REQ, SPEC, CHECK, RULE, TEST, SCEN and CRIT, and recommended AC, which pairs with STORY as user story and acceptance criteria. Owner:

"Need or needs? But I guess ac is the best choice"
