---
type: Decision
id: DEC-22
title: 'Commits and pushes: ask before every push, push only on green; one task per commit, task id in the title, Session trailer; repo is public'
actor: owner
decision_status: PROVISIONAL
decided: 2026-10-10
session: 2026-10-10a
body_sha: sha256:ff03d30bbc28ebb175e9544f6ce7460fb1b653b278bc95aaf9fc27f5fbe3c6a3
---

The owner, 2026-10-09 and 2026-10-10 (session 2026-10-10a), answering the agent's questions on the `Session:` commit line and the push rule:

> also i was told somewhere it says the repo is private? it is now public.
>
> commit messages can carry session or task id, whichever makes more sense, or the message can carry one and the title the other, what do you recommend

The agent recommended: the task id in the title (`CE-n: what changed`), a `Session: <key>` trailer on every agent commit, and a `Closes: CE-n` trailer when a commit finishes a task (FRAMEWORK §6.10, §6.11). It noted that GitHub Actions minutes are free on a public repo, so the reason given for asking before pushes once CI exists no longer held, and asked whether to keep asking.

> still ask before pushes, and push only if the gate is green. commit whenever progress is made and hopefully the gate is green but we can delay that if its a really huge thing that can't be done in smaller steps
>
> minimally one commit per task means each commit is for one task so i guess yes the task id shuld be in the commit title, since there should only be one task
>
> if tasks are small, do a few at once, then get the gate green, then do partial commits for each, but you don't need to be too surgical
>
> the task doesn't need to be ce-... right? the task id acronym can be something else?

So:
- **The repo is public** (since before 2026-10-09). Text that says private is corrected; history keeps what was true then.
- **Pushes: always ask first, and push only on a green gate.** This replaces "push whenever while the repo has no CI" (DEC-13's push clause). Every push still gets a CI watcher.
- **Commits: whenever progress is made, gate green where possible.** A red commit is allowed only for a really huge change that cannot be split into smaller steps.
- **One task per commit; the task id leads the title** (`CE-n: what changed`). Commits that serve no task (records, session close) have a plain title.
- **Small tasks may be done together:** get the gate green over all of them, then commit each task's paths separately. Not surgical: a shared file goes with whichever task fits best.
- **Every agent commit ends with a `Session: <key>` trailer**; a commit that finishes a task also carries `Closes: <task id>` (the agent's recommendation, not objected to).
- **The task prefix is per repo**: `[kinds.task] prefix` in `context.toml`. `CE` is this repo's; another repo picks its own (zanzibar used `TK`).
