# Decisions

Generated from each decision's frontmatter by `context-engine decision index`; never edit it by hand (G-D6).

## BUILT

### adoption

- [DEC-5](DEC-5-framework-before-migration.md): Build the framework and engine before migrating existing repos *(owner, 2026-10-08)*

### assurance

- [DEC-11](DEC-11-sabotage-rule-mandate.md): Sabotage rule is an owner mandate: no test or guard is believed until seen red *(owner, 2026-10-08)*

### charter

- [DEC-10](DEC-10-charter-confirmed-whole-framework.md): Charter confirmed, widened to the whole framework; a managed server is an anti-goal; dogfood here before any other repo *(owner, 2026-10-08)*

### docs

- [DEC-3](DEC-3-framework-spec-tracked-here.md): The framework spec lives in this repo, tracked *(owner, 2026-10-08)*

### dogfood

- [DEC-7](DEC-7-dogfood-manual-mode.md): This repo uses the framework now, by hand, in the v0.5 record shapes *(owner asked, 2026-10-08)*

### housekeeping

- [DEC-4](DEC-4-script-or-mcp-before-edit-subagents.md): Try a script or MCP before edit subagents *(owner, 2026-10-08)*

### packaging

- [DEC-1](DEC-1-own-repo-own-env.md): The engine lives in its own repo and its own env, and is pointed at target repos *(owner + agent, 2026-10-08)*
- [DEC-2](DEC-2-extract-a-package.md): Extract a standalone package; port ideas, not zanzibar's task.py *(owner + agent, 2026-10-08)*
- [DEC-8](DEC-8-mcp-sdk-2-and-ruamel.md): Target the MCP Python SDK 2.x and ruamel.yaml *(agent (claude-opus-5-5), 2026-10-08)*

### principles

- [DEC-12](DEC-12-p15-no-context-agent.md): FRAMEWORK P15: design for an agent that starts with no context *(owner, 2026-10-08)*

### working-state

- [DEC-14](DEC-14-ce-2-working-state-calls-one-file-ledger-baton.md): CE-2 working-state calls: one-file ledger, baton and pause kinds, orient cap 6000 B *(agent (claude-opus-5-5), 2026-10-08)*

### untagged

- [DEC-24](DEC-24-a-baton-is-closed-by-baton-done-with-evidence.md): A baton is closed by baton done with evidence, from any session *(owner, 2026-10-10)*
- [DEC-42](DEC-42-the-adhoc-trial-runs-in-adhoc-s-own-folder-on.md): The adhoc trial runs in adhoc's own folder, on main; the worktree is deleted *(owner, 2026-10-14)*

## PROVISIONAL

### adoption

- [DEC-6](DEC-6-adhoc-first.md): First trial repo: adhoc-microphone-array; intervals second *(agent (claude-opus-5-5), 2026-10-08)*

### delegation

- [DEC-16](DEC-16-several-tasks-in-one-session-one-subagent-per.md): Several tasks in one session: one subagent per task, the top level only reports *(owner, 2026-10-09)*

### naming

- [DEC-15](DEC-15-one-name-context-engine-the-cli-command-and-the.md): One name, context-engine: the CLI command and the MCP server; tools use underscores *(owner, 2026-10-09)*

### records

- [DEC-13](DEC-13-corrections-are-bracketed-insertions.md): Corrections to append-only records are bracketed insertions; the typed words always survive *(owner, 2026-10-08)*

### untagged

- [DEC-17](DEC-17-ultracode-has-standing-approval-when-used-to.md): Ultracode has standing approval when used to minimize token consumption *(owner, 2026-10-09)*
- [DEC-18](DEC-18-avoid-fable-subagents-unless-requested-or.md): Avoid fable subagents unless requested or really necessary; never fan out with fable *(owner, 2026-10-09)*
- [DEC-19](DEC-19-framework-md-is-kept-current-as-we-build.md): FRAMEWORK.md is kept current as we build; archive only what the future must reference *(owner, 2026-10-09)*
- [DEC-20](DEC-20-every-programmatic-process-has-a-ritual-based.md): Every programmatic process has a ritual-based fallback (business continuity) *(owner, 2026-10-09)*
- [DEC-21](DEC-21-section-12-3-answers-q-f-q-g-q-h-defaults.md): Section 12.3 answers: Q-F, Q-G, Q-H defaults accepted; Q-J deferred; no housekeeping write budget by default (Q-K) *(owner, 2026-10-09)*
- [DEC-22](DEC-22-commits-and-pushes-ask-before-every-push-push.md): Commits and pushes: ask before every push, push only on green; one task per commit, task id in the title, Session trailer; repo is public *(owner, 2026-10-10)*
- [DEC-23](DEC-23-versioning-engine-major-minor-is-the-framework.md): Versioning: engine major.minor is the framework version it implements; G-D0 compares major.minor; contract says framework: 0.5 *(owner, 2026-10-10)*
- [DEC-25](DEC-25-if-the-mcp-server-is-not-set-up-the-agent-sets.md): If the MCP server is not set up, the agent sets it up, falls back to the CLI, and asks the owner to restart *(owner, 2026-10-10)*
- [DEC-26](DEC-26-framework-md-holds-the-framework-only-history.md): FRAMEWORK.md holds the framework only; history and owner answers archived *(owner, 2026-10-11)*
- [DEC-27](DEC-27-inv-n-is-the-id-prefix-for-residual-risk.md): INV-n is the id prefix for residual-risk register entries *(claude-code/claude-opus-5-5, 2026-10-12)*
- [DEC-28](DEC-28-ce-7-imports-adhoc-d-27-as-built-narrowed-by-d.md): CE-7 imports adhoc D-27 as BUILT, narrowed by D-29 *(owner, 2026-10-13)*
- [DEC-29](DEC-29-abandoning-a-stale-session-stub-stays-a-by-hand.md): Abandoning a stale session stub stays a by-hand rule for now; the window moves to 3 later sessions counted from last activity *(owner, 2026-10-13)*
- [DEC-30](DEC-30-ultracode-stays-a-judgement-grant-in-the.md): Ultracode stays a judgement grant in the contract, not the setting; the MCP instructions tell agents to ask for it when it would help *(owner, 2026-10-13)*
- [DEC-31](DEC-31-a-session-closes-by-default-when-its-requested.md): A session closes by default when its requested work is done *(owner, 2026-10-13)*
- [DEC-32](DEC-32-the-sessionstart-hook-goes-in-the-machine-local.md): The SessionStart hook goes in the machine-local settings file; init merges it into an existing one after asking *(owner, 2026-10-13)*
- [DEC-33](DEC-33-ce-25-design-criteria-are-rows-one-id-form-a-z.md): CE-25 design: criteria are rows; one id form [A-Z]+-[1-9][0-9]* so goals become G-n; a criterion's actor is its source's; draft planned criteria for US-10, US-12, US-13; split CE-25, guards first *(owner, 2026-10-13)*
- [DEC-34](DEC-34-every-owner-question-carries-a-recommendation.md): Every owner question carries a recommendation, when one is cheap to reach *(owner, 2026-10-13)*
- [DEC-35](DEC-35-this-repo-dogfoods-the-whole-framework-as-it-is.md): This repo dogfoods the whole framework as it is built, the CE-38 bootloader first *(owner, 2026-10-13)*
- [DEC-36](DEC-36-the-engine-commits-at-milestones-not-at-every.md): The engine commits at milestones, not at every write; CE-55 builds it *(owner, 2026-10-13)*
- [DEC-37](DEC-37-imported-ids-are-renamed-at-adoption-keeping.md): Imported ids are renamed at adoption, keeping the number, and each old id stays a resolvable alias (ASK-5 option c) *(owner, 2026-10-13)*
- [DEC-38](DEC-38-standard-id-prefixes-one-readable-prefix-per.md): Standard id prefixes: one readable prefix per record kind in every repo, 2 to 5 capitals; tasks take a per-repo prefix *(owner, 2026-10-13)*
- [DEC-39](DEC-39-rituals-are-renamed-procedures-the-framework-s.md): Rituals are renamed procedures; the framework's strange turns of phrase are corrected in one sweep *(owner, 2026-10-13)*
- [DEC-40](DEC-40-ac-42-decision-import-renames-an-id-in-another.md): AC-42: decision import renames an id in another prefix (DEC-37) instead of refusing it; the rest of AC-42 unchanged *(owner, 2026-10-14)*
- [DEC-41](DEC-41-a-target-repo-s-engine-env-is-a-pinned-install.md): A target repo's engine env is a pinned install kept inside that repo's folder *(owner, 2026-10-14)*
- [DEC-43](DEC-43-start-ce-64-ce-77-ce-78-and-ce-81-now-ce-7.md): Start CE-64, CE-77, CE-78 and CE-81 now; CE-7 waits until next week *(owner, 2026-10-14)*
- [DEC-44](DEC-44-the-top-level-session-coordinates-told-to-do.md): The top-level session coordinates: told to do, check or verify something, it sends an agent *(owner, 2026-10-14)*
- [DEC-45](DEC-45-resume-2026-10-14g-s-fan-out-as-proposed.md): Resume 2026-10-14g's fan-out as proposed; watcher details into CE-83; file a follow-up-session link task; coordinator picks the order *(owner, 2026-10-15)*
- [DEC-46](DEC-46-push-main-once-the-ce-78-and-ce-77-merges-are.md): Push main once the CE-78 and CE-77 merges are committed and both gates are green *(owner, 2026-10-15)*
- [DEC-47](DEC-47-rules-principles-and-decisions-cite-the.md): Rules, principles and decisions cite the incident that justified them *(owner, 2026-10-15)*
- [DEC-48](DEC-48-who-decides-is-set-by-reversibility-a-call-that.md): Who decides is set by reversibility: a call that is cheap to undo is the agent's *(owner, 2026-10-15)*
- [DEC-49](DEC-49-framework-md-holds-what-is-needed-to-understand.md): FRAMEWORK.md holds what is needed to understand and use the framework, not its history *(owner, 2026-10-15)*
- [DEC-50](DEC-50-traps-live-where-their-lifetime-matches-ce-29.md): Traps live where their lifetime matches (CE-29); CE-92 is released from the CE-7 hold, CE-93 stays held *(owner, 2026-10-15)*
- [DEC-51](DEC-51-onboard-audio-workspace-now-as-a-full-migration.md): Onboard audio-workspace now as a full migration; vitest and smoke at push, not per commit *(owner, 2026-10-17)*
- [DEC-52](DEC-52-ce-98-the-decision-importer-fix-is-done-under.md): CE-98, the decision importer fix, is done under DEC-51's lift of the kit hold *(owner, 2026-10-17)*
- [DEC-53](DEC-53-audio-workspace-keeps-its-d-n-decision-ids-on.md): audio-workspace keeps its D-n decision ids on import *(owner, 2026-10-17)*
- [DEC-54](DEC-54-audio-workspace-retires-handoffshape-and.md): audio-workspace retires handoffShape and decisionsIndex, rewrites claudeMdShape, keeps docLinks, architectureShape, runbookShape *(owner, 2026-10-17)*
- [DEC-55](DEC-55-audio-workspace-open-issue-folders-become-tasks.md): audio-workspace open issue folders become tasks, a HANDOFF row naming a folder is that folder's task; the issues archive is routed history *(owner, 2026-10-17)*
- [DEC-56](DEC-56-audio-workspace-prunes-claude-md-and-handoff-md.md): audio-workspace prunes CLAUDE.md and HANDOFF.md to the kit caps; a raised cap only as a dated cutover stopgap *(owner, 2026-10-17)*
- [DEC-57](DEC-57-audio-workspace-s-unattributed-decisions-import.md): audio-workspace's unattributed decisions import with an explicit unrecorded actor; amendment sub-headings fold under their parent *(owner, 2026-10-17)*
- [DEC-58](DEC-58-audio-workspace-engine-gate-is-tsc-lint-over.md): audio-workspace engine gate is tsc + lint over scope all; vitest and smoke stay before push by the runbook *(owner, 2026-10-17)*
- [DEC-59](DEC-59-audio-workspace-task-prefix-aw-sessionstart.md): audio-workspace task prefix AW, SessionStart hook merged, backup by bundle and commit hash, no tag *(owner, 2026-10-17)*
- [DEC-60](DEC-60-the-coordinator-runs-every-task-through.md): The coordinator runs every task through ultracode subagents, even a single task, and is the default whenever the board is worked *(owner, 2026-10-19)*
- [DEC-61](DEC-61-audio-workspace-is-never-pushed-during-its.md): audio-workspace is never pushed during its migration (demo hold): the cutover stays local *(owner, 2026-10-19)*
- [DEC-62](DEC-62-audio-workspace-cutover-goes-today-on-a-local.md): audio-workspace cutover goes today on a local branch; asks LATER; engine commits exempt; charter and stories as drafts *(owner, 2026-10-19)*
- [DEC-63](DEC-63-go-ahead-with-ce-60-item-2-ce-58-ce-65-ce-83.md): Go ahead with CE-60 item 2, CE-58, CE-65, CE-83 and CE-91; CE-83's three open points stay as written *(owner, 2026-10-20)*
- [DEC-64](DEC-64-ce-99-rerank-milestone-is-the-framework-fully.md): CE-99 rerank: milestone is the framework fully built; tasks carry required goals; the agent applies moves, the owner approves drops *(owner, 2026-10-20)*
- [DEC-65](DEC-65-lift-the-kit-hold-for-ce-99-build-it-next-the.md): Lift the kit hold for CE-99; build it next (the recommendation of ASK-15) *(owner, 2026-10-20)*
- [DEC-66](DEC-66-a-replaced-reconstruction-is-re-confirmed-by.md): A replaced reconstruction is re-confirmed by asking the owner again, never by quoting earlier words (the recommendation of ASK-16) *(owner, 2026-10-20)*
- [DEC-67](DEC-67-inv-51-keeps-its-old-title-no-g-w13-alias-the.md): INV-51 keeps its old title; no G-W13 alias (the recommendation of ASK-17) *(owner, 2026-10-20)*
- [DEC-68](DEC-68-ce-99-the-last-rerank-line-lives-in-the-charter.md): CE-99: the last-rerank line lives in the charter; task goals are a G-I1 check on open tasks *(claude-code/claude-opus-5-5, 2026-10-20)*
- [DEC-69](DEC-69-abandoning-a-stale-session-stub-becomes-an.md): Abandoning a stale session stub becomes an engine op, run by start-of-session housekeeping past DEC-29's window, without the owner's word *(owner, 2026-10-22)*
- [DEC-70](DEC-70-finish-the-adhoc-re-pin-to-the-fixed-engine.md): Finish the adhoc re-pin to the fixed engine rather than roll back *(owner, 2026-10-22)*
- [DEC-71](DEC-71-adhoc-s-coordinator-section-goes-after-its-2026.md): adhoc's coordinator section goes, after its 2026-10-17 owner words are recorded as an adhoc decision; adhoc follows the contract *(owner, 2026-10-22)*
- [DEC-72](DEC-72-lift-the-ce-7-kit-edit-freeze-push-finish-ce-79.md): Lift the CE-7 kit-edit freeze; push, finish CE-79, and work CE-113 and CE-93 *(owner, 2026-10-23)*
- [DEC-73](DEC-73-a-delegated-ruling-keeps-the-owner-s-words.md): A delegated ruling keeps the owner's words above a ## Ruling section and names who ruled in ruled_by *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-74](DEC-74-a-delegated-ruling-s-actor-is-owner-asked-lint.md): A delegated ruling's actor is 'owner asked'; lint refuses only a lone owner or human actor *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-75](DEC-75-g-i3-is-a-new-guard-for-delegated-rulings-not-a.md): G-I3 is a new guard for delegated rulings, not a clause of G-I2, and skips superseded decisions *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-76](DEC-76-where-ruled-by-shows-the-question-s-answered.md): Where ruled_by shows: the question's answered mapping, the log line, the decision index, the kit contract and the schema *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-77](DEC-77-delegated-ruling-provenance-applies-going.md): Delegated-ruling provenance applies going forward; a frozen record is fixed by recording again and superseding *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-78](DEC-78-framework-md-s-pre-rewrite-archive-is-named.md): FRAMEWORK.md's pre-rewrite archive is named FRAMEWORK-v0.5-2026-10-23.md *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-79](DEC-79-release-notes-and-pointers-for-cut-text-live.md): Release notes and pointers for cut text live outside FRAMEWORK.md, since AC-33 keeps ids out of it *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-80](DEC-80-engine-internals-move-from-framework-md-to-docs.md): Engine internals move from FRAMEWORK.md to docs/engine.md *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-81](DEC-81-build-status-leaves-framework-md-for-the-board.md): Build status leaves FRAMEWORK.md for the board: Not checked sentences and board items, no generated status table yet *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-82](DEC-82-ce-93-s-rewrite-changes-no-rule-and-no-section.md): CE-93's rewrite changes no rule and no section number; DEC-50's trap-lifetime rule waits for CE-29 *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-83](DEC-83-framework-5-5-rule-5-keeps-the-tree-hash-lock.md): FRAMEWORK 5.5 rule 5 keeps the tree-hash lock standard; the per-repo lock is a deviation filed as CE-135 *(claude-code/claude-opus-5-5, 2026-10-24)*
- [DEC-84](DEC-84-ce-126-fix-subagent-op-line-mis-filing-with-a.md): CE-126: fix subagent op-line mis-filing with a lane field (option B), kept at LATER *(owner, 2026-10-26)*
- [DEC-85](DEC-85-session-2026-10-30a-work-the-board-unattended.md): Session 2026-10-30a: work the board unattended through ultracode, fable's opinion on the rerank, then push *(owner, 2026-10-30)*
- [DEC-86](DEC-86-raise-the-fan-out-runbook-s-g-d1-max-lines-from.md): Raise the Fan-out runbook's G-D1 max_lines from 90 to 110 *(agent (claude-opus-5-5), 2026-10-30)*
- [DEC-87](DEC-87-ac-53-s-provenance-list-names-ruled-by.md): AC-53's provenance list names ruled_by *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-88](DEC-88-a-decision-text-holding-amendments-is-refused.md): A decision text holding ## Amendments is refused at the write, through G-I3's shared check *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-89](DEC-89-new-criterion-ac-101-for-ce-138-s-refusals-not.md): New criterion AC-101 for CE-138's refusals, not a rewrite of AC-98, AC-99 or AC-100 *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-90](DEC-90-g-i3-s-blind-spot-gets-a-register-entry.md): G-I3's blind spot gets a register entry *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-92](DEC-92-linked-batches-reserve-their-ids-with-an-id.md): Linked batches reserve their ids with an id-reserve op, not a batch task new *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-93](DEC-93-ac-33-drops-its-allowance-for-ce-n-build-marks.md): AC-33 drops its allowance for (CE-n) build marks in FRAMEWORK.md *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-94](DEC-94-adopting-repos-get-no-eol-lf-attribute-from-init.md): Adopting repos get no eol=lf attribute from init *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-95](DEC-95-init-appends-the-op-log-merge-union-line-to.md): init appends the op log merge=union line to .gitattributes without asking *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-96](DEC-96-the-5-2-read-first-link-floor-dropped-by-ce-93.md): The §5.2 Read-first link floor dropped by CE-93 returns as a Not checked clause, not as a board item *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-97](DEC-97-the-kit-ships-the-agent-roster-as-framework-6-6.md): The kit ships the agent roster as FRAMEWORK §6.6 text, not as .claude/agents/*.md named agents *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-98](DEC-98-record-confirm-refuses-a-successor-confirmed-in.md): record confirm refuses a successor confirmed in the words that confirmed a story it supersedes; an exact repeat by the owner is quoted with when and where *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-99](DEC-99-ask-new-answered-takes-the-owner-s-words-as-its.md): ask new --answered takes the owner's words as its value, the decision title in --decision-title *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-100](DEC-100-an-answered-question-skips-the-tier-cap.md): An answered question skips the tier cap *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-101](DEC-101-ask-new-answered-is-exempt-from-the-three-part.md): ask new --answered is exempt from the three-part question body check *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-102](DEC-102-the-question-shape-check-lives-in-g-w4-not-a.md): The question-shape check lives in G-W4, not a new guard id *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-103](DEC-103-a-question-s-parts-are-read-mechanically-a-5.md): A question's parts are read mechanically: a 5-word recommendation, two options, a Context part *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-104](DEC-104-a-bare-ask-new-with-no-body-is-refused-the-cli.md): A bare ask new with no body is refused; the CLI takes --body-file *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-105](DEC-105-only-a-closed-session-can-be-followed.md): Only a closed session can be followed *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-106](DEC-106-a-follow-up-names-the-followed-session-in-a.md): A follow-up names the followed session in a follows bullet, not a digest line *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-107](DEC-107-gate-receipt-is-off-by-default-in-the-engine-on.md): gate_receipt is off by default in the engine, on in the kit template and this repo *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-108](DEC-108-task-close-asks-about-residual-risk-through-an.md): task close asks about residual risk through an optional statement plus a reply nudge, not a mandatory flag *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-109](DEC-109-a-residual-stated-at-close-uses-the-design.md): A residual stated at close uses the design-review residual line format plus a required affects field *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-110](DEC-110-task-close-refuses-residual-none-when-the.md): task close refuses --residual none when the design review lists a residual, and its Log names every INV id the close files *(agent (claude-opus-5-5), 2026-10-31)*
- [DEC-111](DEC-111-a-kill-bar-lives-in-a-board-item-s-kill-bar.md): A kill bar lives in a board item's Kill bar section, and task close --verdict is KILL, PASS or VOID with evidence *(agent (claude-opus-5-5), 2026-10-31)*

## SUPERSEDED

### untagged

- [DEC-91](DEC-91-linked-batches-reserve-their-ids-with-an-id.md): Linked batches reserve their ids with an id-reserve op, not a batch task new *(agent (claude-opus-5-5), 2026-10-31)*; superseded by DEC-92

## REJECTED

### storage

- [DEC-9](DEC-9-no-database-source-of-truth.md): No SQLite or other database as the source of truth *(owner, 2026-10-08)*
