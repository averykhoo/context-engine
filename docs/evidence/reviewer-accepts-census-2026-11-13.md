FROZEN: evidence, session 2026-11-13c. A copy of .scratch/fable-review/census.md, made for the owner's question of a reviewer model accepting provisional decisions; not yet a decision.

# Census: owner vs agent decisions (read-only)

Session 2026-11-13c, census actor claude-code/claude-sonnet-census. Data as of 2026-11-13 (341 decision files).
Sources: docs/decisions, docs/ledger/ops.jsonl, docs/ledger/session-log.md, docs/stories.

## 1. Non-owner decisions: outcome and category (243)

Actor is not owner. Outcome is from status, links, ops.jsonl accept ops and amendments. Category is a keyword and id-range heuristic by the census (approximate; judgement calls on ~20%).

| id | actor | status | outcome | category | title | note |
|---|---|---|---|---|---|---|
| DEC-6 | opus(agent) | PROVISIONAL | AMENDED | interpretation of owner words | First trial repo: adhoc-microphone-array; intervals second | owner DEC-10 (reordered), DEC-135 (dropped 2.0.0 wait), 10-13b amend (adhoc ok but audio-workspace wanted) |
| DEC-8 | opus(agent) | BUILT | OTHER | implementation detail | Target the MCP Python SDK 2.x and ruamel.yaml | BUILT, no owner word recorded |
| DEC-14 | opus(agent) | BUILT | OTHER | implementation detail | CE-2 working-state calls: one-file ledger, baton and pause kinds, orient cap 6 | BUILT; owner defaults accepted in DEC-21 |
| DEC-27 | opus(cc) | PROVISIONAL | SUPERSEDED-BY-OWNER | naming-wording | INV-n is the id prefix for residual-risk register entries | informal: owner DEC-38 "What's inv stand for?" -> kit default RISK; INV kept in this repo by alias (fable: keep) |
| DEC-68 | opus(cc) | PROVISIONAL | AMENDED | implementation detail | CE-99: the last-rerank line lives in the charter; task goals are a G-I1 check  | owner words in DEC-64 amendment 2026-10-20f: "Rerank should only run when next is empty" |
| DEC-73 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | A delegated ruling keeps the owner's words above a ## Ruling section and names |  |
| DEC-74 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | A delegated ruling's actor is 'owner asked'; lint refuses only a lone owner or |  |
| DEC-75 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | G-I3 is a new guard for delegated rulings, not a clause of G-I2, and skips sup |  |
| DEC-76 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Where ruled_by shows: the question's answered mapping, the log line, the decis |  |
| DEC-77 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Delegated-ruling provenance applies going forward; a frozen record is fixed by |  |
| DEC-78 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | FRAMEWORK.md's pre-rewrite archive is named FRAMEWORK-v0.5-2026-10-23.md |  |
| DEC-79 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | Release notes and pointers for cut text live outside FRAMEWORK.md, since AC-33 |  |
| DEC-80 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | Engine internals move from FRAMEWORK.md to docs/engine.md |  |
| DEC-81 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | Build status leaves FRAMEWORK.md for the board: Not checked sentences and boar |  |
| DEC-82 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | CE-93's rewrite changes no rule and no section number; DEC-50's trap-lifetime  |  |
| DEC-83 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | FRAMEWORK 5.5 rule 5 keeps the tree-hash lock standard; the per-repo lock is a |  |
| DEC-86 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | Raise the Fan-out runbook's G-D1 max_lines from 90 to 110 | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-87 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | AC-53's provenance list names ruled_by | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-88 | opus(agent) | SUPERSEDED | SUPERSEDED-BY-AGENT | implementation detail | A decision text holding ## Amendments is refused at the write, through G-I3's  | by DEC-125 (DEC-162 endorsed) |
| DEC-89 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | New criterion AC-101 for CE-138's refusals, not a rewrite of AC-98, AC-99 or A | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-90 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | G-I3's blind spot gets a register entry | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-91 | opus(agent) | SUPERSEDED | SUPERSEDED-BY-AGENT | implementation detail | Linked batches reserve their ids with an id-reserve op, not a batch task new | by DEC-92 (same title, agent fix) |
| DEC-92 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | Linked batches reserve their ids with an id-reserve op, not a batch task new | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-93 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | AC-33 drops its allowance for (CE-n) build marks in FRAMEWORK.md | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-94 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | cross-repo or external | Adopting repos get no eol=lf attribute from init | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-95 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | cross-repo or external | init appends the op log merge=union line to .gitattributes without asking | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-96 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | The §5.2 Read-first link floor dropped by CE-93 returns as a Not checked claus | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-97 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | The kit ships the agent roster as FRAMEWORK §6.6 text, not as .claude/agents/* | owner concurred in DEC-162 ("text") |
| DEC-98 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | record confirm refuses a successor confirmed in the words that confirmed a sto | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-99 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | ask new --answered takes the owner's words as its value, the decision title in | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-100 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | An answered question skips the tier cap | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-101 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | ask new --answered is exempt from the three-part question body check | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-102 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | The question-shape check lives in G-W4, not a new guard id | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-103 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | A question's parts are read mechanically: a 5-word recommendation, two options | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-104 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | A bare ask new with no body is refused; the CLI takes --body-file | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-105 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | Only a closed session can be followed | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-106 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | A follow-up names the followed session in a follows bullet, not a digest line | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-107 | opus(agent) | SUPERSEDED | SUPERSEDED-BY-OWNER | implementation detail | gate_receipt is off by default in the engine, on in the kit template and this  | DEC-162 (owner took fable "on") -> DEC-223 |
| DEC-108 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | task close asks about residual risk through an optional statement plus a reply | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-109 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | A residual stated at close uses the design-review residual line format plus a  | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-110 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | task close refuses --residual none when the design review lists a residual, an | owner concurred in DEC-162 ("optional") |
| DEC-111 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | A kill bar lives in a board item's Kill bar section, and task close --verdict  | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-112 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | The decision_status/status agreement check is a clause of G-W4, not a new G-id | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-113 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | G-D3 reads backticked repo paths only in the docs a new [guards] paths list na | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-114 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | scope or priority | Build CE-144 (the optional ambiguous-bare-name check) rather than drop it, in  | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-115 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | Framework build status is generated on demand (context-engine coverage), not k | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-116 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | Criterion writes are not milestones | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-117 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | criterion new writes rows only and never guesses the table | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-118 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | naming-wording | Criterion ids | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-119 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | A write-time twin is off when its guard is off | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-120 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | OKF profile (FRAMEWORK §9.3): build the stale_after refusal and the charter_st | owner concurred in DEC-162 ("cut") |
| DEC-121 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | doc archive names the pointers G-D3 newly reports after a move and rewrites no | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-122 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | Archiving a doc whose frontmatter declares liveness turns that key FROZEN, kee | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-123 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | A partial prune is doc archive --lines A-B, into one <stem>-pruned.md per sour | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-124 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | cross-repo or external | The plugin launcher judges a settings orient hook stale by its program and --r | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-125 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | The ## Amendments refusal at the write covers every append-only kind and is no | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-126 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | record new's refusal of a preset status or SUPERSEDED on a decision is not beh | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-127 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | The task set the owner asked for is a tasks: line in the session's ledger stub | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-128 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | G-W6 also fails the newest close whose tasks: ids are missing from its rows: | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-129 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | hk.close is redesigned, not dropped: it closes only on a git-checked Closes: t | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-130 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | An op log line may carry as, mapping a session-keyed field to the key it was s | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-133 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | interpretation of owner words | INV-31's compaction observation goes to a new dated evidence doc, not the froz | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-136 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Tier-0 housekeeping: the session runs hk run start/close; the hook only shows  |  |
| DEC-137 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | hk comment is tier 0 for Session-trailered commits whose title leads with ids; |  |
| DEC-138 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-6 close-out scope: split hk.ratchet (CE-168) and ledger rotation (CE-169),  |  |
| DEC-139 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | session touch on a stub that is not open names a remedy per stub kind, not one |  |
| DEC-140 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | G-W11 skips only when git says the clone is shallow; a repo without git is sti |  |
| DEC-141 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | hk comment's no-key case is a caller key with no ledger entry, refused with th |  |
| DEC-142 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Single-item hk comment needs no Session: line; the scan lists untrailered id-l |  |
| DEC-143 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | hk run is not a milestone itself; it commits once at its end only when one of  |  |
| DEC-144 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | An hk run phase skips hk stamp when no question kind is configured; its commit |  |
| DEC-145 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | G-W10 counts operations as writes, with the op log lines beside them; the coun |  |
| DEC-146 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-6 close: coverage reading G-W10 as built goes to CE-164; the close clause i |  |
| DEC-159 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | implementation detail | Records are published by an engine read op, site build, as stdlib HTML with bo | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-160 | opus(agent) | ACCEPTED | ACCEPTED-UNCHANGED | cross-repo or external | A config that still sets decision_index loads; nothing reads it, and orient na | bulk op 2026-11-07d (owner DEC-162 took fable digest advice) |
| DEC-164 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | A close that leaves the banner records banner: kept <key>, and G-W1 accepts it |  |
| DEC-165 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | session close runs hk run close, the entry and an optional banner in one batch |  |
| DEC-166 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | session start --continues is a link of its own, beside --follows, and orient r |  |
| DEC-167 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | orient generates the last close and the last push; no review queue until CE-18 |  |
| DEC-168 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Orient serves Last close after the banner, and drops it whole when the banner  |  |
| DEC-169 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | A banner is kept only once a close has written it under CE-195 |  |
| DEC-171 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Co-Authored-By on every engine commit: from --co-author, --model, CE_CO_AUTHOR |  |
| DEC-172 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | context-engine commit adds its trailers to a last paragraph only when it holds |  |
| DEC-174 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | Owner decisions recorded PROVISIONAL before CE-187 are migrated by decision ac |  |
| DEC-175 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Owner-question bodies are read by their part names and list nesting, and task  | agent-amended after verifier FAIL |
| DEC-176 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | A record that does not parse is a lint failure naming it, never a crash (CE-16 | agent-amended after verifier FAIL |
| DEC-178 | opus(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-191: session close warns of an empty NOW on its reply's first line, from th |  |
| DEC-179 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | task new --body-file: an empty file gives the default body |  |
| DEC-180 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | task new: --body and --body-file are mutually exclusive |  |
| DEC-181 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | task new --body-file: no runbook, kit or MCP change |  |
| DEC-182 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Orient parts pinned in manual-mode from source |  |
| DEC-183 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Conditional orient parts as continuations |  |
| DEC-184 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Orient part ranks unpinned |  |
| DEC-185 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | AC-110 row dated |  |
| DEC-186 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Derive OKF status in the Store, not an Engine op (CE-179) |  |
| DEC-187 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | A board item whose status contradicts its state is refused at create, never ov |  |
| DEC-188 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Scope of the status derivation: literal state closed on board kinds only (CE-1 |  |
| DEC-189 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Criterion id allocation counts a superset of lint's rows: every id-led row of  |  |
| DEC-190 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | decision link's refusal of a non-criterion id names the first criteria_rows pr |  |
| DEC-191 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | store.py::Store._criterion_prefixes keeps its own raw regex for now (store.py  |  |
| DEC-192 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | tools/sabotage_ce5.py is already stale at HEAD in 5 rows CE-150 does not touch |  |
| DEC-193 | sonnet(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Pause resume names, never re-applies, the paused session's tasks (CE-152) |  |
| DEC-194 | sonnet(agent) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | The pause resume hint lists only tasks still open and not yet named by the res |  |
| DEC-195 | sonnet(agent) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | ask raised refuses a question id ID_RE cannot read back, before any last_asked |  |
| DEC-196 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | test_ci full-history check requires the integer 0: type(depth) is int and dept |  |
| DEC-197 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | hk comment on a record that is not a board kind is refused as '<id> is a <kind |  |
| DEC-198 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-170 bullet 3 (test the dry branch of Engine._hk_reindex) dropped: the metho |  |
| DEC-199 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | The shallow-clone wording fix also covers Engine._stale_stub_failures and the  |  |
| DEC-200 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | doc freeze writes the FROZEN line when a doc declares no liveness: by default, |  |
| DEC-201 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Freeze placement in a doc with no declaration: after its H1 (past the blank li |  |
| DEC-202 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | doc freeze re-reads its result with G-D4's reading (guards.declared) and refus |  |
| DEC-203 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-155: stale_after is refused at write time by record new, task set and decis |  |
| DEC-204 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-155: the write-time stale_after stop ignores liveness and mirrors lint's bo |  |
| DEC-205 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Write-time G-D3 twin for append-only text (CE-183): record new, ask answer/ask | agent-amended after verifier FAIL |
| DEC-206 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Reserved ids pass the write-time twin only when this session holds them (CE-18 |  |
| DEC-207 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Backticks are the foreign-id form; no repo-qualified id notation (CE-183): rej |  |
| DEC-208 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Backticking a foreign id inside an owner's verbatim quote is markup, not a cha |  |
| DEC-209 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | The check runs before the write, not as lint before the milestone commit (CE-1 |  |
| DEC-210 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | decision import lists sub-headings apart: the dry run's `## Sub-headings kept  |  |
| DEC-211 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | an entry-less log's import refusal names its `###` headings: parse_log stays a |  |
| DEC-212 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | import line numbers are those of the file given: the dry-run doc names that fi |  |
| DEC-213 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-171 part 4 (aliasing a bare unhyphenated id such as D17 at import) is split |  |
| DEC-214 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Duplicate live decision titles are a new intent guard G-I4: not a clause of G- |  |
| DEC-215 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | G-I4 current means not `status: deprecated` (REJECTED and DEFERRED count, as G |  |
| DEC-216 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | G-I4 is lint-only: no write (record new, ask answer, decision set title=) refu |  |
| DEC-217 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | DEC-162 relates/narrows link kind is met by the existing `refs` and `relaxes`/ |  |
| DEC-218 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | Engine default is a named constant: config.py::GATE_RECEIPT holds the kit patt |  |
| DEC-219 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | Explicit '' stays the off switch: gate_receipt = '' turns the check off and an |  |
| DEC-220 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | Test fixtures given matching receipts: fixture ledgers and receipts() quote a  |  |
| DEC-221 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | Remedies name the way out for gates with no pass count: the session close refu |  |
| DEC-222 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | INV-86 left alone: the default keeps the kit's loose 'not run' match; tighteni |  |
| DEC-223 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | gate_receipt is on by default in the engine; '' turns it off |  |
| DEC-224 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Pointer reds are a multiset: doc archive matches G-D3 failures before and afte |  |
| DEC-225 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | A prune never changes the doc's own declaration: `doc archive --lines` refuses |  |
| DEC-226 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Long frontmatter gets a FROZEN key: when the ARCHIVED line would fall past G-D |  |
| DEC-227 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Table and archive file: the redirect table and `<stem>-pruned.md` may carry un |  |
| DEC-228 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Re-read before writing: doc archive re-reads the doc, the archive file and the |  |
| DEC-229 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Kit task prefix: the template holds the placeholder TASK; init on a repo with  |  |
| DEC-230 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Prefix form: init takes 2 to 5 capitals; config load refuses only a prefix tha |  |
| DEC-231 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Lint G-D2 reds a task prefix equal to a standard (DEC, STORY, AC, ASK, RISK, G |  |
| DEC-232 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Goal ids: GOAL-n, G-n and legacy Gn read as one goal by number; a new write mu |  |
| DEC-233 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Register ids: the register's entries' prefix, else the last logged register.ap |  |
| DEC-234 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | Prefix census: init on a new repo warns, never refuses, where a kind prefix al |  |
| DEC-235 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | kit/contract.md keeps its D-4..9 example: changing contract text reds G-D0 in  |  |
| DEC-236 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | naming-wording | The standard and reserved prefix sets live once, in config.py::STANDARD_PREFIX |  |
| DEC-237 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | A push made while no session was open is recorded by a `pushed:` receipt on a  |  |
| DEC-238 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | The `pushed` receipt's form is `<hash>[, <hash>...]: <note>`: 7 to 40 hex char |  |
| DEC-239 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | The acknowledged Upstream line keeps the push state and names the close that r |  |
| DEC-240 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-186 drops only sabotage_ce55's reindex row; its nine other stale rows are f |  |
| DEC-241 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-170's _hk_reindex nit is settled by CE-170's own close; its body is not edi |  |
| DEC-242 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | AC-181's text gains the enum-order and escaped-record-text clauses |  |
| DEC-243 | sonnet(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-186's sabotage rows go in tools/sabotage_ce185.py, not a new script |  |
| DEC-244 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | CE-188: HOLD is a fifth pri tier, last after SOMEDAY, on the task kind only, k |  |
| DEC-245 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | CE-188: held means never ready: G-W5's NOW rule, the task close / session clos |  |
| DEC-246 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | CE-188: the rerank skips HOLD by procedure (step 1 reads no HOLD item, step 2  |  |
| DEC-247 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-190 grant shape: --grant on `ask answer` and `ask new --answered`; the word |  |
| DEC-248 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-190 ledger half: a grant writes a `granted:` stub bullet, carried as a clos |  |
| DEC-249 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-190 grant refusals, before any write: a decision title, a ruling or ruled_b |  |
| DEC-250 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-190: `ask answer` without --grant has its empty title refused by the engine |  |
| DEC-251 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-196: register retire keeps the entry: heading `(retired <session>: <why>)`  |  |
| DEC-252 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-196: Entry.risk is the bare risk with the retired marker parsed off and Ent |  |
| DEC-253 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-196: register retire --into merges: why becomes `merged into <id>[, <why>]` |  |
| DEC-254 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-196: register retire's why is one line without brackets (the heading marker |  |
| DEC-255 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-196: register show counts retired entries in N, adds `, M retired`, prints  |  |
| DEC-256 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-196: G-W13 fails a register entry whose heading marker and `retired:` line  |  |
| DEC-257 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-196: register retire is not a milestone: it rides along, DEC-36's list unch |  |
| DEC-258 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-177: orient detects no MCP server by a mark the server writes on its first  |  |
| DEC-259 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-177: the MCP mark is sticky: written once, never refreshed; deleting it bri |  |
| DEC-260 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-177: orient's MCP notice has no opt-out: rank 2, shown until a tool call wr |  |
| DEC-261 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-177: next_steps puts MCP registration after the kit commit and before sessi |  |
| DEC-262 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-177: contract and FRAMEWORK 11.1 unchanged, no framework bump; 6.9 and 8.0. |  |
| DEC-263 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-177: the MCP mark is machine state in the gitignored lock dir: not op-logge |  |
| DEC-264 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-178: legacy board history is kept on the import op line (as), not exempted  |  |
| DEC-265 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-178: the import path is a new op, task import <file> (JSON Lines of id, fie |  |
| DEC-266 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-178: as on an import line is opt-in (create_many keep_history), so task new |  |
| DEC-267 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-178: a legacy value the schema does not take (a plain date in a session-key |  |
| DEC-268 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-178: task import invents nothing (no defaulted moved, updated, source or bo |  |
| DEC-269 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-178: task import has no --dry-run and is not a commit milestone, as decisio |  |
| DEC-270 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-184: init warns where the checkout converts line endings and writes no git  |  |
| DEC-271 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-184: the line-ending fix the kit names is core.autocrlf=input, not false: u |  |
| DEC-272 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-184: eol_warnings detects by the repo holding .git, core.autocrlf true/yes/ |  |
| DEC-273 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | CE-184: the gate's content id stays byte-exact (no CRLF normalisation in gate. |  |
| DEC-274 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: the op-line lane key is `lane` (DEC-84's word), set from CE_AGENT, the |  |
| DEC-275 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: a lane is any ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ token, not checked aga |  |
| DEC-276 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: every lane is taken by the session close, the session pause AND the pa |  |
| DEC-277 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: the coordinator-only ops refuse a lane: session start, close, pause an |  |
| DEC-278 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: the MCP `agent` parameter is per call only: never remembered in the se |  |
| DEC-279 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: a commit or milestone with no lane takes only unlabelled lines; no new |  |
| DEC-280 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: an unparseable op line's lane is read from its text, and the line stay |  |
| DEC-281 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: G-W7 reds an op line whose `lane` value is malformed |  |
| DEC-282 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-126: no `Lane:` commit trailer |  |
| DEC-283 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | coverage: section 8.0.2's operations become G-D12's fourth class: backticked n |  |
| DEC-284 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | coverage: an operation registered in ops.OPS is owned for G-D12 and built for  |  |
| DEC-285 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | coverage: a G-id with no lint guard reads built when the guards.py::ENFORCED t |  |
| DEC-286 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | coverage: an open board item does not outrank the map's DEFERRED or PROSE-ONLY |  |
| DEC-287 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | coverage map: a new dated map supersedes the 2026-10-12 map, with G-W10 EXISTI |  |
| DEC-288 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-165: a guards receipt's not run counts only when it opens the receipt or is |  |
| DEC-289 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-165: INV-86 is edited in place to the narrowed residual, not retired: the r |  |
| DEC-290 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-165: AC-113's housekeeping Writes cell is pinned to only through hk_ operat |  |
| DEC-291 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-165: AC-160's lock pin asserts the OS lock is held at the read, write and o |  |
| DEC-292 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-175 banner-only commit: a banner.set commit carries HEAD's orientation note |  |
| DEC-293 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-175 given path goes whole: a path given to `context-engine commit` is alway |  |
| DEC-294 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-175 graft scope: the graft applies only when every uncommitted op line nami |  |
| DEC-295 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-175 consequence: a session's own hand edit to HANDOFF.md no longer rides it |  |
| DEC-296 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Gate parts schema: [gate.parts.<name>] = command + required scope, run in decl |  |
| DEC-297 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | Part coverage: every part row records every scope's id; a scope is covered whe |  |
| DEC-298 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | gate run with parts runs every part and continues past a failure, one row per  |  |
| DEC-299 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-181 (b) is fixed by parts plus the close procedure (gate run --stale, then  |  |
| DEC-300 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | gate status, not orient, reports stale parts (hashing the tree at every Sessio |  |
| DEC-301 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | With gate parts, the scope guard keys on the running part's scope (CE_GATE_PAR |  |
| DEC-302 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Housekeeper agent tools: only hk_run and hk_comment, model haiku; the test pin |  |
| DEC-303 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | hk comment --scan lists tier-1 title mentions: a Session commit whose title na |  |
| DEC-304 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | A tier-1 text comment carries its sha: hk comment --text logs <short sha>: <te |  |
| DEC-305 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Tier-1 token count: the harness's figure for the agent run, put by the session |  |
| DEC-306 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | The housekeeper agent belongs to this repo only (.claude/agents/), not the kit |  |
| DEC-307 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | P19 is a new numbered principle at the end of FRAMEWORK §1, pointed at from P7 |  |
| DEC-308 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | A hand-run check is verification, not a P17 control: P19 sends it to the board |  |
| DEC-309 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | framework or contract rule | P19 is enforced by a lint plus a write-time refusal that every manual criterio |  |
| DEC-310 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | cross-repo or external | No kit contract text in CE-194: P19's contract line waits for the next contrac |  |
| DEC-311 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Hazard home is a board row: an unverified hazard is a board task labelled `haz |  |
| DEC-312 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Hazard close refusal: task close refuses a `hazard`-labelled row whose close s |  |
| DEC-313 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Hazard label match: case-insensitive and stripped for the refusal; task list - |  |
| DEC-314 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Hazard route: a new 'Unverified hazards' [[routes]] entry on tasks in context. |  |
| DEC-315 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-29 memory split: the memory half is filed as its own task (or CE-29 kept op |  |
| DEC-316 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | scope or priority | CE-193 pick-up 2026-11-08: entry 3 done, no task; 5 and 10 one task; 11 a bug; |  |
| DEC-317 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | CE-40 deliverable shape: one evidence doc docs/evidence/global-claude-md-audit |  |
| DEC-318 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | Trimmed global CLAUDE.md keeps machine and harness facts verbatim, adds a fram |  |
| DEC-319 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | Global-vs-framework divergences (subagent model default, HANDOFF read in full, |  |
| DEC-320 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | GAP rules (.scratch sweep four classes, auditor's own report dir, eager commit |  |
| DEC-321 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | interpretation of owner words | CE-40 closes once its doc is committed and verified (doc freeze, then task clo |  |
| DEC-322 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | CE-18 build-or-defer: rollback and close is designed (FRAMEWORK 6.13) and done |  |
| DEC-323 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | process or workflow rule | Rollback and close undoes records by their operations and files by path, never |  |
| DEC-328 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | The size floor's durable home is FRAMEWORK §6.6; the frozen advice doc is not  | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-329 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | The size floor is the coordinator rule's one exception in FRAMEWORK §6.6 and P | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-330 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | A reading-tier builder only for a pinned code task that changes neither FRAMEW | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-331 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | Every fix from the second FAIL on runs on the most tier; the verifier is never | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-332 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | The one trial metric kept: an `escalated:` task comment per escalation | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-333 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | The roster gains a planner row; a new criterion pins the build ladder | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-334 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | fan-out.md gets one pointer sentence; no cap is raised | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-335 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | framework or contract rule | Question triage written into the spec and procedures: decision shape, arbiter  | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-336 | sonnet(agent) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | ask decide: what an owner-authored source is, no dead actor check, SUPERSEDED  | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-339 | opus(cc) | ACCEPTED | ACCEPTED-UNCHANGED | process or workflow rule | Design of the CE-231 headroom fixes and G-D13, the guard that keeps record ids | bulk op 2026-11-13a (fable review DEC-337, owner DEC-340) |
| DEC-341 | opus(cc) | PROVISIONAL | STILL-PROVISIONAL | implementation detail | CE-225 design: plan check reuses G-D3's span verdicts, and a (new) mark exempt | agent-amended after verifier FAIL |

Mixed-actor decisions (not counted above): DEC-1 (owner + agent, BUILT; AMENDED by owner DEC-41), DEC-2 (owner + agent, BUILT; unchanged), DEC-7 (owner asked, BUILT; agent note only), DEC-148 and DEC-149 (owner asked, ruled by opus, ACCEPTED, unchanged), DEC-162 (owner asked, ruled by fable, PROVISIONAL: the fable-advice adoption).


## 2. Owner pushback, reversals and reshaping of agent calls

Method: formal links (supersedes/amends, amendments, ops.jsonl accept/supersede ops) first, then every owner-actor decision, story and amendment read for corrections, then a text scan for "why", "nvm", "instead", "hold on", "don't need". Most agent calls were never reviewed per item by the owner (see section 3), so most pushback below comes from chat-level corrections that the owner's own decisions record (the agent call is often a proposal, a task design or an execution, not a DEC id). Quotes are verbatim from the cited records.

### 2a. Formal: an agent DEC was changed or overridden

| agent id | owner artifact | owner words | what changed | kind |
|---|---|---|---|---|
| DEC-107 (gate_receipt off by default) | DEC-162 (owner asked, ruled by fable) -> built as DEC-223 | "okay take fables recs, and push when the gate is green" (fable rec: "on"; CE-187 log: "the owner overruled it") | superseded; default flipped to ON | substantive correctness; the reasoning came from the fable reviewer, not the owner |
| DEC-68 (rerank trigger in charter) | DEC-64 amendment 2026-10-20f | "Rerank should only run when next is empty" | "Superseded in part": trigger conditions removed (owner_mark, newer_than removed) | wrong trigger / token cost |
| DEC-6 (adhoc first, intervals second) | DEC-10 (ASK-1); DEC-6 amendment 2026-10-13b; DEC-135 | "Adhoc is a good repo yes, we'll do a quick trial there, but I'm hoping to get this into the audio workspace repo soon, since that's a better testing ground" | order amended: dogfood here first; adhoc waits; later the intervals 2.0.0 wait dropped | priority/scope |
| DEC-27 (INV-n prefix) | DEC-38 (owner, 2026-10-13c); fable advice (CE-56 rename half: no) | "What's inv stand for? ... we might as well choose something easy to understand." | kit default became RISK; this repo keeps INV through the DEC-37 alias | naming taste |
| DEC-1 (engine in own env; mixed actor) | DEC-41 | "the engine should run within the adhoc repo so thats where everything should exist." | amends where a target repo's engine env lives | design/location preference |
| DEC-88, DEC-91 | agent's own DEC-125, DEC-92 | n/a (DEC-162 endorsed 88 -> 125) | SUPERSEDED-BY-AGENT, owner-endorsed | agent self-correction |
| DEC-175, DEC-176, DEC-205, DEC-341 | agent coordinator after an opus verifier FAIL (amendments) | n/a | agent calls amended after an independent verifier found false refusals or holes; DEC-341 call 4 changed | reviewer-model catching real defects (agent on agent) |

### 2b. Informal: owner reshaped, reversed or questioned an agent proposal or action (not a DEC id; the owner decision that records it is cited)

| # | agent call | owner artifact | owner words | kind |
|---|---|---|---|---|
| 1 | charter scoped to the record engine only | DEC-10 / US-9 | "i think a server i have to start and manage is not just a non-goal, its an anti-goal" ; "is that all we're doing? the end goal is to build the entire system" | scope too narrow / misread intent |
| 2 | ASK-2 `correct` framed as any text change | DEC-13 | "What sort of correction does ask-2 cover? Just typos? ... the goal is intent not bug for bug equivalence" | over-broad proposal; owner narrowed it |
| 3 | DEC-16 read "A single-task request is unaffected" | DEC-44, DEC-60 (and DEC-16 amendment 2026-10-20b) | "even if there is only one task, don't do the task yourself" | agent read the owner's rule too narrowly |
| 4 | after the repo went public, agent asked whether pushes still need asking | DEC-22 | "still ask before pushes, and push only if the gate is green" | agent proposed relaxing a guard; refused |
| 5 | MCP set-up needed a CE_PYTHON env var | DEC-25 | "Actually nvm, let's try to find a better way." (session log: "Owner asked why the MCP server needs CE_PYTHON") | design too complex |
| 6 | stale-stub window 2 sessions | DEC-29 | "Maybe extend that to 3 later sessions." | parameter tweak |
| 7 | init would not merge into existing hook settings (ASK-4) | DEC-32 | "Why isn't merging the recommended approach? Is there some concern?" | agent too cautious |
| 8 | CE-45: every engine write commits itself | DEC-36 | "do we really need to commit at every write? every task completion yes" | process overreach; reshaped to milestones |
| 9 | framework wording "rituals" and odd turns of phrase | DEC-39 | "look for strange turns of phrase, and correct them all at once" | wording taste |
| 10 | adhoc trial set up in a worktree | DEC-42 | "oh wait no it needs to be in the actual folder, not a separate worktree" | execution vs intent (the worktree followed the owner's own 2026-10-13b words) |
| 11 | audio-workspace gate ran vitest and smoke on every commit | DEC-51 | "don't think we need that or the smoke test every commit" | too heavy |
| 12 | backup tag in the migration plan | DEC-57/58/59 | "Why a tag? Just a commit is fine? Does the tag do anything?" | unnecessary step |
| 13 | migration plan pushed a tag | DEC-61 | "so don't push that repo at all" | plan conflicted with a hold |
| 14 | audio-workspace start no earlier than Wednesday (another repo's agent) | DEC-62 | "Go today, no AW session" | timing/priority |
| 15 | rerank trigger "NOW empty", then "NOW and NEXT empty" | DEC-64 | "why do you recommend now empty over now plus next? ... the prioritization is slightly expensive token wise" then "Rerank should only run when next is empty" | cost; rejected twice |
| 16 | housekeeping write budget (Q-K) | DEC-21 | "i'm not sure we need a budget" | over-engineering |
| 17 | session left open "since you may want to keep going" | DEC-31 and amendment | "Close the session, and add a rule to close by default when the work is done" | too passive |
| 18 | README citing tasks and ids; records hand-written by muse | DEC-338 | "Hold on why is readme citing tasks? Isn't readme supposed to be really just something useful to read?" | misread intent / taste, plus process bypass |
| 19 | co-author trailer left to agents | DEC-170 | "Make the cli command add the header so it's always there." | omission; owner wants mechanical enforcement |
| 20 | sonnet builders without a planner (DEC-173 trial shape) | DEC-177 | "an opus agent should write or at least see the plan" | quality reshape |
| 21 | ASK-36 about zanzibar token allow rules and tag push | DEC-157 | "nevermind, just leave the tokens and tag push behavior for now" | unneeded escalation |
| 22 | agents keep asking | US-24, DEC-48, DEC-34 | "get fables opinion instead of asking me, if it can be decided from first principles ... or if it can be reversed without too much cost ... just go ahead" ; "who decides can be set by reversibility" | standing policy: fewer owner questions |
| 23 | FRAMEWORK.md carried history and build status | DEC-26, DEC-49 | "not what's needed to be a historian" | scope creep / taste |
| 24 | stored decision index.md | US-19 | "Why do we need an index md when it could be a command?" | legacy design |
| 25 | agent roster had no arbiter | DEC-18 amendment | "This is one of the rare situations where I do ask for a fable subagent" | owner added a role (additive) |
| 26 | (counter-example) owner wanted zanzibar next | DEC-134 | "Okay let's add Zanzibar as a task bit do intervals first" | owner yielded to the agent's evidence |

### 2c. Where the owner accepted the agent's recommendation as given (ASK answers)

Of the 38 ASK records, about 31 are answered "Recommended" / "okay to your recommendation" / "yes" (DEC-33 parts 3, 5-7; DEC-37, 40, 52-59, 65-67, 69-71, 84, 131, 132, 135, 147, 150-156, 161, 324, 325). About 6 were reshaped or dismissed (ASK-1, 2, 3 part 4, 4, 13 in part, 36). DEC-148 and DEC-149 were delegated back to the agent ("Yes finish the intervals migration and cutover").

### 2d. Standing owner policy that bears directly on a reviewer model

- US-24 (owner, 2026-11-06/09/10; ASK-38 option A): decide a derivable question with fable's opinion instead of asking; if reversible and not direction-changing, "just go ahead with something reasonable even if you or fable aren't fully sure".
- DEC-48: who decides is set by reversibility: "opus (or fable) should be able to make the call".
- DEC-335 and DEC-336 (agent, accepted): triage and `ask decide` already built around that.
- Precedent for a reviewer standing in for the owner: DEC-162 (owner adopted fable's advice on the 2026-11-06b queue: ~60 accepts, 4 single calls, 1 supersede) and DEC-337/DEC-340 (fable design review of DEC-328..336, all nine ENDORSE; owner: "Ok to all"). In both, the owner changed nothing except where fable said to; one agent call (DEC-107) was flipped, on the reviewer's reasoning.


## 3. Counts

### 3a. Decisions by actor class (341 files, 2026-10-08 to 2026-11-13)

| actor class | n | notes |
|---|---|---|
| owner | 92 | 83 ACCEPTED, 8 BUILT, 1 REJECTED (DEC-9). Owner decisions are born ACCEPTED since CE-187 |
| owner asked (ruling delegated) | 4 | DEC-7 (BUILT), DEC-148/149 (ACCEPTED, ruled by opus), DEC-162 (PROVISIONAL, ruled by fable) |
| owner + agent | 2 | DEC-1, DEC-2 (BUILT) |
| agent, non-owner | 243 | 163 claude-code/opus (new actor form), 62 "agent (claude-opus-5-5)" (old form), 14 claude-code/sonnet, 4 "agent (claude-sonnet-5-5)" |

### 3b. Non-owner (agent) decisions by outcome (n = 243)

| outcome | n | share |
|---|---|---|
| ACCEPTED-UNCHANGED | 52 | 21% |
| STILL-PROVISIONAL (never reviewed) | 180 | 74% |
| STILL-PROVISIONAL, owner concurred (DEC-97, 110, 120 in DEC-162) | 3 | 1% |
| AMENDED by owner words (DEC-6, DEC-68) | 2 | 0.8% |
| SUPERSEDED-BY-OWNER (DEC-107 formal; DEC-27 informal) | 2 | 0.8% |
| SUPERSEDED-BY-AGENT (DEC-88, DEC-91) | 2 | 0.8% |
| OTHER (BUILT: DEC-8, DEC-14) | 2 | 0.8% |

By actor form and outcome: opus(cc) 151 PROVISIONAL, 10 ACCEPTED, 1 AMENDED, 1 SUPERSEDED-BY-OWNER; opus(agent) 41 ACCEPTED, 15 PROVISIONAL, 2 SUPERSEDED-BY-AGENT, 2 OTHER, 1 AMENDED, 1 SUPERSEDED-BY-OWNER; sonnet(cc) 14 PROVISIONAL; sonnet(agent) 1 ACCEPTED, 3 PROVISIONAL.

Caveat that matters for the reviewer idea: all 52 ACCEPTED were accepted in two bulk ops (2026-11-07d: 42 agent decisions, after DEC-162 took fable's digest-based advice; 2026-11-13a: DEC-328..336 and 339, after fable's design review and DEC-340 "Ok to all"). No agent decision has an owner per-item acceptance. So "accepted unchanged" measures reviewer-model endorsement plus owner delegation, not independent owner agreement. The 180 PROVISIONAL are mostly DEC-179..323 (CE-build design calls, 2026-11-08), and the session log carries the open item "owner: review the PROVISIONAL decisions DEC-179..DEC-323".

Of the 61 agent decisions that got any review (52 accepted, 3 concurred, 2 amended, 2 superseded-by-owner, 2 superseded-by-agent), 4 were changed by owner words (6.6%); only 1 (DEC-107) was a reversal of substance, and it came through the fable reviewer. Over all 243: 4 changed by the owner (1.6%).

Mixed-actor: DEC-1 AMENDED by owner (DEC-41); DEC-2, DEC-148, DEC-149 unchanged; DEC-162 PROVISIONAL.

### 3c. Pushback rate per category

Formal (agent DEC changed by owner words), category denominators are the 243 agent decisions (category by id-range heuristic, approximate):

| category | agent DECs | owner-changed | rate | ACCEPTED-UNCHANGED |
|---|---|---|---|---|
| implementation detail | 89 | 2 (DEC-68, DEC-107) | 2.2% | 24 |
| process or workflow rule | 69 | 0 | 0% | 13 |
| cross-repo or external | 21 | 0 | 0% | 4 |
| framework or contract rule | 20 | 0 | 0% | 8 |
| scope or priority | 16 | 0 | 0% | 1 |
| interpretation of owner words | 15 | 1 (DEC-6) | 6.7% | 1 |
| naming-wording | 13 | 1 (DEC-27) | 7.7% | 1 |

Informal (the 25 owner corrections in 2b plus the 5 formal owner-changed items, 30 total, by category; no clean denominator because most were chat-level proposals, not DEC ids):

| category | cases |
|---|---|
| process or workflow rule | 10 (#4, 6, 8, 15, 16, 17, 19, 20, 22, 25) plus DEC-68 |
| cross-repo or external (adoption of adhoc, audio-workspace, zanzibar) | 7 (#10-14, 21, DEC-1) |
| implementation detail | 4 (#5, 7, 24, DEC-107) |
| framework or contract rule | 3 (#2, 18, 23) |
| scope or priority | 2 (#1, DEC-6) |
| naming-wording | 2 (#9, DEC-27) |
| interpretation of owner words | 1 (#3) |

Pattern by kind: over-engineering / unnecessary step / too heavy (#8, 11, 12, 16, 24, 23, 5): 7; agent too passive or too cautious (#7, 17, 19, 21-22 reversed direction): 3 to 5; taste, naming, wording (#9, 18, DEC-27): 3; scope or reading of owner words too narrow (#1, 3): 2; timing/priority (#14, DEC-6, #15): 3; substantive correctness reversal: 1 (DEC-107).

### 3d. What the data supports and does not

- Supports: the owner's corrections cluster on process weight (too many commits, tags, budgets, per-commit test runs, stored indexes), on naming and wording taste, and on reading owner rules too narrowly. Almost no correction targets a code-level implementation call.
- Does not support: any rate for the 180 unreviewed agent decisions. There is no recorded owner reaction to them.
- Agent-on-agent review has real signal: 4 PROVISIONAL decisions (DEC-175, 176, 205, 341) were amended after an opus verifier FAIL; DEC-88 and DEC-91 were self-superseded; fable's DEC-107 flip.

## 4. Maturity snapshot (as of 2026-11-13)

- Goals: 7 (G-1..G-7), held as rows in `docs/charter.md` (charter_status: confirmed 2026-10-08, DEC-10), not as separate records; each has a "Measured by" column. Stories per goal: G-7 10, G1 5, G5 5, G6 5, G3 4, G4 4, G2 2 (stories still use legacy `G1` form in `goals:`; lint reads it as G-1).
- Stories: 24 (US-1..US-24), all actor owner; 23 `story_status: live`, 1 `unspecified` (US-22).
- Unspecified or thin stories:
  - US-22 (unspecified): one sentence, "scheduled tasks"; goal G-3; no design, no criteria.
  - US-12: owner says "i havent really thought through this so just write it down first"; "Not built"; amendment: "just be a task, i don't need it built right now".
  - US-13: "Not designed, not built"; owner unsure how git fits.
  - US-18: one line, no verbatim header, no notes.
  - US-16, US-20, US-21: one or two sentences each (US-20 and US-21 are audio-workspace feedback items).
  - US-2, 6, 7, 8: one-line owner questions answered by the agent; thin as intent, but built.
- Other: 178 acceptance-criteria rows in `docs/criteria.md`; 274 task/ASK files (192 closed, 44 open, 38 ASK); 341 decisions; 1 REJECTED decision (DEC-9).
- Caveat on stories: 13 carry an explicit "Owner's words (verbatim)" heading (count measured 2026-11-13 by grep); the others quote the owner inline. No story says anything about reviewer models or auto-acceptance; the nearest are US-24 and DEC-48 (section 2d).
