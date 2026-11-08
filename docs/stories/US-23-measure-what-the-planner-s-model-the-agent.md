---
type: Story
id: US-23
title: Measure what the planner's model, the agent split and compaction do to cost and quality
actor: owner
story_status: live
goals: [G-1]
date: 2026-11-08
body_sha: sha256:74586ee85c08c39e33dc2b5502e47cf683ade622e4fb6d7a348551710ce7ce95
---

Owner, 2026-11-08 (session 2026-11-07e):

> Maybe we burn a few tokens and run a sonnet planner in parallel and get another agent to compare the plans? Just to see if the planner makes a difference, and if so then with what kind of tasks - I'm pretty sure there's a difference but I don't have numbers or stats
>
> Is 100k tokens times 5 agents or 500k tokens with 1 agent better? 250k times 2?I'm not sure how caching works with Claude's api so I'll need you to figure out the optimization, and there's also context rot to be concerned about. I haven't looked into auto compaction though, that might help with tokens more than divide and conquer, and the extra compacted context might produce better results? Or maybe it'll forget or start getting things wrong, not sure how it'll go, maybe it needs an experiment
>
> Mechanical tasks to haiku is good but is there a way to cut down the 30k context? Although I guess for haiku it's not super important hmmm, tokens are cheap, but maybe can we keep the haiku agent around, run compact, and get it to do all the mechanical tasks?

Earlier in the same exchange, the owner asked: "How's it going, and how's the opus planner doing relative to sonnet? Or is that not really part of the tasks being run now? If not then nvm, but anything we can do to minimize token cost or improve out ones is welcome. Also what do you think haiku might be good for"
