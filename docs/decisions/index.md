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

## REJECTED

### storage

- [DEC-9](DEC-9-no-database-source-of-truth.md): No SQLite or other database as the source of truth *(owner, 2026-10-08)*
