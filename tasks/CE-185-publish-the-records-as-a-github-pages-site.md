---
type: Task
id: CE-185
title: Publish the records as a GitHub Pages site built by CI; remove the stored decision index
brief: US-19; engine read op, not a CI script; gate.yml untouched; nothing stored
pri: NEXT
state: closed
deps: []
goals: [G-5]
source: session 2026-11-06a
created: 2026-11-06
moved: 2026-11-06a
updated: 2026-11-06a
review: [shipped, guard]
status: deprecated
closed: 2026-11-06a
---

Publish the records as a GitHub Pages site built by CI, and remove the stored decision index (US-19).

Owner, 2026-11-06a: "okay yes can you get the pages deployed and the index removed? we can do it all in one session".

Scope:
- An engine read op (`site build <outdir>`, CLI and MCP) that renders a static site from the records (decisions grouped as the index was, stories, the board, coverage, the register; record ids as links) and stores nothing in the repo. It lives in the engine, not in a CI script, so adopters on other hosts (GitLab Pages) wrap the same op.
- `.github/workflows/pages.yml`: on push to main, run the op and deploy with actions/deploy-pages. `gate.yml` is untouched. GitHub Pages is already on for the repo (build_type workflow, turned on through the API 2026-11-06a): https://averykhoo.github.io/context-engine/
- Remove `docs/decisions/index.md`, its regeneration on every decision write (`[working] decision_index`, store.py::Store._reindex), `hk regen_index` / `decision index` as a stored write, and G-D6's decision-index check; keep the grouped listing as a read.
- FRAMEWORK §6.5, §9.3, §8 (G-D6) and the runbooks (kit copies byte-equal) updated in place; README links the site.
- A test that the built site holds every record id, seen red under sabotage (DEC-11).

Why: the index was carried over from the v0.4 single-file log (audio-workspace decisionsIndex.mjs); OKF v0.2 §8 makes index.md optional ("consumers MAY synthesize one on the fly") and §11 says consumers MUST NOT reject a bundle for a missing index.md; stories and tasks already have none. DEC-115 rejected a write-regenerated stored table for the same reason (it couples concurrent sessions through commits).

## Traps

- none yet

## Read first

- decisions.py::render_index
- store.py::Store._reindex
- ops.py::coverage
- docs/decisions/DEC-115-framework-build-status-is-generated-on-demand.md
- tests/test_ci.py

## Log

- 2026-11-06a (claude-code/claude-opus-5-5): closed: Records site live on GitHub Pages; stored decision index removed
  residual risk: INV-95, INV-96, INV-97

## Design review

affects: every adopting repo (its context.toml sets `decision_index` and it holds a stored index), the owner and anyone reading the records on GitHub without the CLI, the next session (the `hk_regen_index` tool and the stored index are gone)
- eliminated: the stored index going stale after a hand edit or a by-hand decision, and concurrent sessions colliding through commits of one generated file (DEC-115's reason): nothing generated is stored
- reduced: an adopter's context.toml refusing to load once `decision_index` is no longer read | rung: reduce | control: config.py keeps accepting the key as deprecated, and orient's `Deprecated config` section names the remedy (DEC-160; tests/test_site.py::test_a_deprecated_decision_index_still_loads_and_orient_names_the_remedy)
- reduced: the site leaving out a record, or linking to a page it does not hold | rung: reduce | control: tests/test_site.py::test_the_site_holds_every_record_and_every_link_resolves, run by the gate on every commit
- reduced: `site build` writing into the tracked tree, so the output gets committed and is the stored index again | rung: reduce | control: site.py::build refuses a directory inside the repo that git does not ignore, and a non-empty one (tests/test_site.py::test_site_build_refuses_a_tracked_or_non_empty_directory)
- residual: an adopter's stored index.md goes stale until someone acts on orient's notice | rung: individual | why: deleting a tracked file in another repo is that repo's owner's call, not the engine's | control: orient's `Deprecated config` section (DEC-160)
- residual: the published site is only as current as the last deploy, and a failed deploy shows only in GitHub Actions | rung: collective | why: GitHub runs the deploy, outside the gate | control: the CI watcher every push gets (procedures § Push and CI)
F: a new record kind or link field needs a line in site.py; the id test goes red when a kind's records stop appearing; the pages workflow's action versions age like gate.yml's
A: the records stay plain markdown, readable on GitHub without the site; `context-engine decision index` prints the grouped listing; manual-mode § context-engine site build says what the site holds
M: one engine op that CLI, MCP and CI all call; the id-and-link test; tests/test_ci.py pins pages.yml to the Python floor and to the op
E: reuses decisions.render_index's grouping, guards.framework_status's rows and review.entries for the register; one runbook section; stdlib only
