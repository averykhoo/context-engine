---
type: Decision
id: DEC-159
title: Records are published by an engine read op, site build, as stdlib HTML with bodies as escaped text; CI deploys it; nothing is stored
actor: agent (claude-opus-5-5)
decision_status: PROVISIONAL
tags: [publishing]
tasks: [CE-185]
decided: 2026-11-06
session: 2026-11-06a
body_sha: sha256:1afb43509dda024f6d0f58b35abd6a7aac666d70609f7fc89a13d204bcebce5b
---

**Call** (agent, CE-185, on US-19): the records are published as a static HTML site that the engine builds with a read op, `context-engine site build <dir>` (MCP `site_build`), and that `.github/workflows/pages.yml` deploys to GitHub Pages on every push to `main`. Nothing it builds is stored in the repo.

- **One engine op, not a CI script.** CLI, MCP and CI call the same function (`site.py::build`), so a repo on another host (GitLab Pages) wraps the same op in its own job, and the site cannot drift from what the engine reads.
- **Stdlib only.** The pages are generated HTML: the decisions grouped as the stored index was (`decisions.py::groups`, shared with `decision index`), the stories by status, the board by tier with every closed item, the coverage table (`guards.py::framework_status`) and the register (`review.py::entries`), one page per decision, story and board item. A record's body is shown as its markdown text, escaped and wrapped, not rendered: no markdown library is taken, required or optional, so the gate tests exactly what CI publishes.
- **Ids become links** wherever the site holds the record (and `INV-n` in the register), and so do URLs; other ids stay text.
- **It never writes into the tracked tree.** The output directory must be new or empty, and outside the repo or git-ignored in it, or the op refuses: a committed build would be the stored index again.

**Alternatives considered.**
(a) A CI-only script (a Python step in pages.yml). Rejected: an adopter on another host would copy it, and it would read the records without the engine's parsing.
(b) Render markdown with the `markdown` package as an optional extra, degrading to escaped text without it. Rejected for now: a second rendering path the gate does not run, for prettier prose. Reopen if the owner wants rendered bodies.
(c) A static-site generator (Jekyll, MkDocs) over the markdown files. Rejected: a toolchain outside the engine, and it shows files, not records (no grouping by status, no board).
(d) Keep the stored index beside the site. Rejected by US-19: the site is what makes it unnecessary.

**Reopen if:** the owner wants rendered markdown, search, or pages for kinds the site leaves out (batons, pauses, criteria).
