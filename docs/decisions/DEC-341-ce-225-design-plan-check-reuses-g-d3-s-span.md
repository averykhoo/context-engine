---
type: Decision
id: DEC-341
title: "CE-225 design: plan check reuses G-D3's span verdicts, and a (new) mark exempts what a plan creates"
actor: claude-code/claude-opus-5-5
decided: 2026-11-13
session: 2026-11-13a
decision_status: ACCEPTED
body_sha: sha256:bbefbc20158193b7231703819f4c6bb8a8e7505795ad8706e01e976d7dcabaed
---

The planner's design calls for CE-225, the plan-citation check DEC-327 trials (its idea 2). An agent's calls, cheap to undo: PROVISIONAL until the owner reviews them.

1. **An engine operation, `plan check <path>` (MCP `plan_check`), read-only.** It sits in the Checks group of FRAMEWORK §8.0.2 beside `lint`, so every adopted repo and every agent has it over the CLI and the MCP. Rejected: a `lint --plan` flag (lint would then run every guard, and fail on unrelated reds, before the plan's answer); a script under `tools/` (no MCP tool, and adopted repos do not have it).

2. **One resolution, shared, not copied.** The bodies of G-D3's two span checks become three helpers in guards.py: `code_ref_verdict` (the `links` half: `code_ref_problem`, then `ambiguous_problem`), `is_pointer` (the `path_pointers` shape test) and `path_verdict` (the `path_pointers` resolution, from the repo root or the citing doc's directory). `links`, `path_pointers` and the new `plan_problems` all call them, so the plan check cannot drift from G-D3, and the existing G-D3 tests guard the move. Rejected: a new loop that calls the same primitives (two copies of the order of checks); G-T3's `existence` resolution (its messages differ and it does not read the doc's own directory).

3. **What is a citation.** Every backticked span outside fenced code and frontmatter that G-D3 reads as a `file::symbol` or a path pointer; blockquotes and history lines count too (a plan is fresh, and its builder reads every line of it). Not citations, by G-D3's own shapes: globs, placeholders, spans with spaces, URLs, a leading `.` or `/`, and anything outside backticks; another repo's path or an example is written without backticks, as G-D3's remedy already says. A plan inside the repo also resolves a path from its own directory; a plan outside the repo resolves from the repo root only.

4. **The mark for what a plan creates: ` (new)` right after the span**, at most one space or tab between, lower case. It exempts every citation of that path, of a path under it, of the same bare file name, and, for a `file::symbol`, of that symbol and the dotted names under it, wherever it stands in the plan; nothing else (a sibling file, a name that only starts the same). Rejected: a `## New files` section (a builder reading one line cannot see it); a prefix inside the backticks (it breaks the span as a citation for every other reader, G-D3 included); refusing a `(new)` path that already exists (after the build the plan would fail, so a re-check in a fix round would go red for no fault).

5. **Ambiguous counts as failing**, as it does in G-D3: a bare name matching files whose texts differ leaves the builder to guess.

6. **A plan that cites nothing fails (exit 1)**, unless it marks something new: a check that read nothing must not pass, and a pinned plan names every file it changes. Exit codes: 0 all resolve, 1 any fails or nothing was cited, 2 a refusal (no such plan file), as lint's.

7. **Where the ladder says it runs:** FRAMEWORK §6.6, the build ladder's step 1: after the planner and before any builder; a plan it fails goes back to the planner. Not in the fan-out runbook: it points at the ladder already and is 10 bytes under its cap, so a copy there would mean moving text out for a sentence that duplicates the spec.

## Amendments

- **2026-11-13a (claude-code/claude-opus-5-5):** Call 4 changed (the coordinator's call, claude-code/claude-opus-5-5, after CE-225's first verifier report, still PROVISIONAL): a ` (new)` mark exempts a path, what is under it and its bare name only while that path does not exist. A marked path that exists (`path_exists`, `path_verdict`'s own test: case-exact from the repo root or the plan's directory; a bare name, any repo file of that name) is not new: its mark exempts nothing, so every citation under it is checked as usual, and the mark itself is listed as a problem (`marked (new) but exists: mark the new symbols (or files) in it instead`). A plan that adds to an existing file marks each new `file::symbol`, not the file.

  Why: the verifier found two holes in call 4 as built. `src/context_engine/guards.py` (new) on an existing file let `guards.py::no_such_qq` pass (rc 0), and a bare-name mark such as `__init__.py` (new) exempted every repo file of that name and their symbols. Of the two narrow fixes, exempting nothing silently, or reporting the mark, the mark is reported: a planner who believes an existing file is new has misread the code, the very thing the check is for, and may have the builder write that file afresh over what is there; a silent no-op would hide that.

  What it costs, the reason call 4 first gave: a plan re-checked after its build reports the mark of each path the build created. The check's place is before the build (FRAMEWORK §6.6, the build ladder's step 1), so this is accepted; a fix round that re-plans checks the new plan before its build, as the first. A `file::symbol` marked new whose symbol already exists is still not checked.
