---
type: Story
id: US-19
title: Records are published as a GitHub Pages site built by CI, so no human-readable index is stored
actor: owner
story_status: live
goals: [G-5]
via: Claude Code chat session 2026-11-06a
date: 2026-11-06
body_sha: sha256:86d8088e3d024feace62cecd90c57b0fbd9bdb8f26dd7cb943458e770f854b3d
---

## Owner's words (verbatim)

> Why do we need an index md when it could be a command?

> why do we require it? is this just legacy design? is it just for humans looking at it without cli, in github?

> hmm what if there was a github ci that deployed pages built from the okf stuff in this repo? then the readme could just link it, and i wouldn't need human readable indices at all

> can you use my github token from the zanzibar repo to help me set it up, i don't want to go to my pc now

> okay yes can you get the pages deployed and the index removed? we can do it all in one session

## Notes

AGENT: said in chat in sessions 2026-11-05a/2026-11-06a, after the agent found that the decision index (`docs/decisions/index.md`) was carried over from the v0.4 single-file log and that OKF v0.2 §8 makes `index.md` optional ("consumers MAY synthesize one on the fly"). In response to the fourth message, the agent turned on GitHub Pages for averykhoo/context-engine (build_type workflow, https://averykhoo.github.io/context-engine/) through the API on 2026-11-06, using the stored github.com credential.
