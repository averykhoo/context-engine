FROZEN. A verbatim copy of adhoc-microphone-array's context-engine-feedback.md at adhoc bfea740, copied 2026-10-21a on the owner's word (CE-7). Everything below this line is adhoc's text, unedited.

# context-engine feedback: after-action review

An after-action review of working AD-16 (joint segmentation and localization for background
talkers) through context-engine. It starts with session 2026-10-16b, where one top-level session
coordinates multi-agent workflows. Entries are added while the work runs and finished at the
session close.

## Owner's instructions for this process

> (owner, 2026-10-16: "The end goal is to do them all, can you be the coordinator over ultracode
> subagents and get them to use sub sub agents, I don't need it fast, just token efficient, so use
> sonnet for simple things and haiku for babysitting-without-fixing if applicable")

> (owner, 2026-10-16: "Also create a new md file in this repo, context-engine-feedback.md and we'll
> do an aar of those whole process and put it in there. Also note my previous statement of using
> cheap babysitter agents in there")

> (owner, 2026-10-17: "One more thing for context engine feedback, always assume the main convo
> should be a coordinator and manage ultracode, farming any task out to a subagent, even if there
> is only one task. When all mentioned tasks are completed, automatically close the opened session
> without waiting for confirmation.")

> (owner, 2026-10-17: "Hoes progress on ad16? Can we get it done? Coordinate ultracode and get as
> far as you can. I'll be a bit busy so just get fable to make any decisions for now")

> (owner, 2026-10-19: "Is the stuff from that session done? Can you close that session?")

> (owner, 2026-10-21: "Anything that's recorded about the context framework but not in the
> feedback md?")

> (owner, 2026-10-21, after seeing the gap list: "Yup put it all in there")

The 2026-10-17 delegation is quoted from AD-16's log (`tasks/AD-16-*.md`, entry 2026-10-17a) and
DEC-80; the 2026-10-19 question from the ledger's 2026-10-17a entry.

How the first instruction is applied:
- **The top-level session coordinates.** It writes one workflow per round of AD-16's ladder. It
  owns every record write (task, decision, ask, session), every commit and every verdict. Workflow
  agents may run only read-only engine queries (`task show`, `decision show`).
- **Each task's chain is spelled out in the workflow script:** implement, review, a long run,
  watch, write-up. Implementers may hand bulk reading to their own sonnet subagents (the "sub sub
  agents").
- **Model per job:**
  - Implementers inherit the session model.
  - Reviewers, launchers of already-written runs, and write-ups use **sonnet**.
  - Watchers of long compute runs use **haiku**. They only watch: no fixing, re-running, killing
    or relaunching. This is the owner's "cheap babysitter" rule. The global rule for CI watchers is
    the same: watch only, and report a verdict per run.
- **Every agent persists its report incrementally** to `.scratch/ad16/<task>-<step>.md`.

## Timeline

- **2026-10-16b start.**
  - The `SessionStart` hook printed `orient` (no session).
    - **Update (2026-10-21):** this startup print is the only one of the four live hook probes
      that any record here shows. The ledger's 2026-10-14a and 2026-10-14b entries list "INV-31
      live probes ... orient on startup, resume, /clear, compaction" as still owed. The item then
      dropped off every later "Still owed" list without being run, and no tracked file records a
      resume, `/clear` or compaction probe (grep of the tree, 2026-10-21).
  - `session start` gave key 2026-10-16b.
  - Orient listed one other open session: 2026-10-16a, fable, the one that wrote DEC-76 and
    AD-16's plan. ASK-10 was raised in chat and marked with `ask raised`.
- **Round 1 workflow** (`ad16-round1`, run `wf_a169f1e6-fe5`) runs AD-19 and AD-22 in parallel:
  - **AD-19:** rung 1, the go/no-go gate for AD-16.
  - **AD-22:** the far-talker generator option and its ceiling ladder.
  - **Each track's chain:**
    - The implementer, then a sonnet review loop of at most two fix rounds.
    - Sonnet (AD-19) or the inherited model (AD-22) launches the detached run.
    - A haiku watcher waits on it.
    - A sonnet agent writes up the results.

- **The owner closed two open threads.**
  - "No sessions running except you", so 2026-10-16a's stub was marked `kind: abandoned` by hand.
    The engine has no operation for this yet (procedures § Housekeeping).
  - "I guess no harm trying that for ad13": `ask answer ASK-10`. This wrote DEC-77, closed ASK-10
    and unblocked AD-13 in one command, and committed it as `1e99226`.
- **AD-13 workflow** (`ad13-fresh-prereg`, run `wf_ba20abbc-19b`):
  - **Review:** one D-31 review by a Fable agent. Fable was used because
    `vetting/hidden/README.md` records that a Fable review is owed before any pre-registered use;
    it is a single agent, never a fan-out.
  - **Fix:** an inherited-model agent fixes what the review blocks on. It stops instead of fixing if
    a fix would move the dev844 numbers that DEC-77 rests on.
  - **Pre-registration:** written into a results file before any reserved seed is rendered.
  - **Check:** sonnet checks the pre-registration against DEC-77 and the draft bars.
  - **Not launched:** the coordinator commits the code first, so the md5s the pre-registration
    names are the ones that run.

The bullets below were added on 2026-10-21 (see the Addendum).

- **2026-10-17a (died).**
  - Opened 19:05:02 on the owner's delegation (Owner's instructions above). It raised ASK-11 and
    ran round 1 as workflow `wf_e77db043-981`, in which fable ruled on ASK-11.
  - From about 19:18 a chain of nested `bash.exe` grew to about 2,550 processes. At about 20:39
    the laptop hit its commit limit and every detached run died of `MemoryError` (items 19, 20).
  - The session itself died about 20:55, with no close and no pause. Its four op lines stayed
    uncommitted until 2026-10-19 (item 22).
- **2026-10-19a (recovery, close, then a hand-abandon).**
  - Opened 10:32:13. Its first engine commit, `a24d18d`, recorded DEC-80 (fable's ruling,
    transcribed from the dead workflow) and carried the dead session's op lines (items 22-24).
  - Round 1 resumed as workflow `wf_118c4497-19e`; the killed runs resumed by scene. AD-24's fresh
    judgement on seeds 929-1000 was KILLed on bar 3, and DEC-80's stop clause parked AD-16.
  - The session closed itself at 20:10 (`9f7a5a7` banner, `bb0892b` close), as item 17's rule
    asks. Then, at the owner's question, 2026-10-17a was marked abandoned by hand in `5c61449`
    (20:45), after that close (item 25). The close's ledger entry says "Nothing pushed."
- **2026-10-20 (a push outside any session).** A full gate ran into `.scratch/gate/` from 19:03 to
  19:14, then `444efcc..5c61449  main -> main` was pushed at 19:14. No session was open, and no
  record mentions it (item 26).
- **2026-10-21a (this gap audit).** Opened 07:56:58. The owner asked what was recorded about the
  framework but missing here. A read-only audit answered, and on the owner's word its findings
  became items 19-36 and the dated updates to older entries.

## Observations

What worked, what got in the way, and what the engine could do differently. Each entry is marked
**engine** (a context-engine issue), **process** (how the session ran the work) or **repo** (this
repo's records).

1. **engine: orient cannot say whether another open session is live.** It lists 2026-10-16a as
   open, but a session that ended without `session close` looks the same as one still editing the
   tree. The owner has to be asked. A last-activity time (the newest op line or commit by that
   session) would answer it most of the time.
2. **repo: a dangling section reference inside a record.** AD-19's body cites "DEC-76, 'Where this
   leaves the signature'", and DEC-76 has no section with that title (its nearest is "Why the
   current detectors miss them" or "The method to try"). Lint checks routes and record schemas, not
   references to a section inside another record, so this passed the gate.

3. **engine: no operation to abandon a stale session.** The owner's word was enough to retire
   2026-10-16a, but the step was a hand edit of the ledger heading. A `session abandon <key>
   --why` that writes the owner's words and files batons would keep this in the engine's
   append-only path.
   - **Update (2026-10-21):** it has now happened three times, 2026-10-15 to 2026-10-19.
     2026-10-14d was marked abandoned by hand in 2026-10-15a (before this review began),
     2026-10-16a in 2026-10-16b, and 2026-10-17a in 2026-10-19a. The last went in as a plain
     commit, `5c61449` (20:45), after 2026-10-19a's own `session close` (`bb0892b`, 20:10), so a
     closed session's key signs it. None of the three has an op line: `docs/ledger/ops.jsonl` has
     no abandon op (2026-10-21).
4. **engine (good): `ask answer` did four things in one command.** It wrote the decision, closed the
   question, unblocked the task and committed. No by-hand step was needed.
5. **process: sequencing across workflows is the coordinator's job.** AD-13's fresh render needs the
   generator. That is the same `scripts/synth_scenes.py` AD-22 is changing in round 1, so the fresh
   render waits until AD-22's change is reviewed and committed. The workflow API cannot express a
   dependency between two runs, and the engine's task `deps` are not visible to workflows. So the
   AD-13 workflow was cut at "prepare, do not launch".

6. **process: the haiku babysitters did not babysit (round 1).** Both watchers returned within
   about a minute, reporting `finished: false`; one wrote "expected ~20 min". Each had been given
   one long open-ended wait, and they ended the turn instead of blocking. The cost moved upward:
   - AD-19's sonnet write-up agent waited out the run itself: 44 min, 143k tokens, three polling
     rounds.
   - AD-22's write-up agent gave up and returned "INCOMPLETE", so round 1b had to re-watch the
     run.

   Fix (round 1b): the workflow script owns the loop. Each haiku watcher makes ONE bounded blocking
   call of 9 minutes or less, then returns `finished` and `alive`, and the script re-spawns watchers
   until the run finishes or dies (16 tries at most). A cheap tier needs the loop in deterministic
   code, not in its own judgement.
7. **process: a pre-registered kill bar written by an agent needs a coordinator check before it
   retires tasks.**
   - **The bar.** AD-19's bar ("AUC < 0.7 for every tier") did not say which AUC. The implementer
     chose "same vs host" after a 2-scene smoke, and disclosed that. It is the conservative choice,
     and it fired KILL (best 0.629).
   - **The flag.** The kept talkers, the control, reach only about 0.78 AUC vs anyone, which points
     at a weak measurement rather than unidentifiable people.
   - **What was done.** The coordinator kept the verdict as written and ran a measurement-validity
     diagnostic, reported apart from it. The diagnostic adds an image-signal arm (the ceiling
     perfect host removal could give) and TDOA error for kept and lost talkers, solo and overlapped.
     The owner decides whether AD-16 stops.
   - **Engine angle.** Nothing in the engine links a results file's pre-registered bar to the task
     whose fate it decides. A `task close --verdict <results file § n>` would make that link
     auditable.
8. **process: a generator option can change the base scene it is added to.** AD-22's far talkers
   take over turns of the base timeline, and 5 near talkers lost their only turn. Seeds with too
   small a room are skipped (13 of 892-928). The reviewer passed it: old plans stay byte-identical
   with the option off, which is the invariant CLAUDE.md states. But "adding a feature leaves every
   older draw unchanged" does not cover the option being ON. The results file has to say this.

9. **process (good): the D-31 Fable review earned its cost on AD-13.** It found the blocking gap
   before any reserved seed was rendered (213k tokens). Test (c) existed only in gitignored-adjacent
   vetting scripts. No tracked path scored the revival arm. And passing the obvious callable,
   `events.event_prob`, silently accepts nothing. A sonnet check of the pre-registration came back
   clean, and a one-scene dry run matched the stored dev844 run on 55 checks. The driver refuses to
   start until the code it names is committed with the md5s the pre-registration records. That is a
   mechanical guard, not a doc warning.
10. **engine: G-D1 caught CLAUDE.md growth at once.** Adding the far-talker rule took CLAUDE.md
    82 bytes over its 19000-byte cap, and lint went red. The remedy text was actionable, and the
    rule was cut to four lines. The cap does its job of keeping the contract small.
    - **Update (2026-10-21): the cap now stops rules from landing.** On 2026-10-19 the AD-7 fix
      agent added the bullet "One voice per talker is opt-in (AD-7, DEC-<NEW>, 2026-10-19)" to
      CLAUDE.md. Lint went red, G-D1 "335 lines / 19450 bytes over the Contract caps 330 / 19000".
      The bullet was removed and deferred; only the stream-list wording stayed (now CLAUDE.md
      line 190, "8 `--speech-corpus` speakers (AD-7, DEC-81)"). Source: the agent's gitignored log
      `.scratch/ad16-r1/ad7-fix2.md`, Steps 2 and 4. CLAUDE.md is 18883 of 19000 bytes and 327 of
      330 lines (2026-10-21), so 117 bytes are left. Two durable rules have no tracked home:
      the owner's coordinator rule (item 17) is only in auto-memory, and the crash rule (item 20)
      is tracked only in this file. G-D1's remedy is to cut. It names no place for a rule to move to
      (a runbook, say), so a full contract makes rules that arrive later fall out.

11. **process: the looped haiku watchers worked, mostly, and one false alarm cost a sonnet turn.**
    - **Round 1b:** 11 AD-22 watch rounds of about 9 minutes, each 47-53k tokens.
    - **The false alarm:** watch11 reported the run `alive: false` seconds after the driver
      started its next stage's workers, a race in `kill -0` on the MSYS pid. The loop then handed
      over to the sonnet write-up. It correctly found the run alive and wrote nothing tracked, but
      the round's write-up was spent.
    - **Lesson:** a watcher that sees the process dead should confirm twice, a minute apart,
      before returning.
    - **A cheaper babysitter than haiku:** the coordinator's own `run_in_background` shell
      until-loop on the stage file costs no tokens until it exits and wakes the session. Inside a
      workflow, haiku is still the right tier, because workflow agents cannot be woken by a
      background job.
    - **Update (2026-10-21): a second false alarm, from the watcher's own timeout.** On
      2026-10-19, during AD-24's fresh run, the tool call watching step 6's shard 1 hit the 2-hour
      tool limit. The write-up first recorded that the shard had "outlived its wrapper's 2-hour
      tool limit". Fable's audit corrected it: "only the tool call watching the wrapper hit the
      limit. The wrapper itself ran to completion (its own `sep q1 rc=0`, `end 19:58:49` lines
      are in stage.txt)" (`docs/results/2026-10-17-ad16-bout-verifier.md` § 10). The data was not
      affected. **Lesson:** a watcher that times out says nothing about the run it watches. Read
      the run's own stage file before writing anything down.
12. **process (good): the post-verdict diagnostic changed the owner's question.** AD-19's KILL
    stands as pre-registered. The diagnostic shows the clean image clears the bar on 6 of 8
    variants (TDOA 0.96-0.99) where the mixture clears none, and 43% of overlapped bouts lock onto
    the host. So the question for the owner is no longer "stop AD-16?" but "is the kill bar
    measuring the right thing?". A coordinator that had closed the tasks on the mechanical verdict
    would have retired the lever the evidence points at.
13. **process: a subagent ran a non-script file through bash.** It came from a shell-variable slip
    in a Git Bash heredoc. Backticked text in a markdown file was executed, and stray files
    landed in the Git install folder. The agent found its own stray files and deleted them, and it
    found another left there by an earlier session's identical slip. The global CLAUDE.md
    two-shell section warns of the PowerShell-in-Bash direction. This is a third failure mode
    worth a line: **never `bash <file>` a path held in a variable without checking its
    extension**.

14. **engine: recording an owner's answer to a question asked through the chat tool has no
    one-step path.** ASK-10 had an ask record, so `ask answer` did everything at once. The AD-16
    question was put through the chat question tool, with no ask record behind it, so it needed a
    hand-built `record new decision --set ...` with five keys and a body file. It worked first
    time, and lint was clean. An `ask new --answered "<owner words>"` (open and answer in one step)
    would keep owner decisions taken in chat on the same rails.
15. **process: a mechanical summary line can read as the opposite of its table.** AD-13's driver
    printed "All six DEC-77 bars: FAIL." when 4 of 6 passed. It meant the all-six rule failed. The
    sonnet write-up read the table correctly, and the coordinator checked it against `summary.md`.
    A verdict line should name the failing bars ("FAIL: bars 2, 3").
16. **process (good): DEC-77's fresh test was run cleanly and decided as written.**
    - **The chain:** pre-registration, a D-31 review fix, a commit, md5 guards, a single run,
      `ALLDONE ok`, and bars applied as written.
    - **The result:** FAIL (net +1, bar 2 wants +2). Of the 24 lost people, only one was ever a
      candidate. So the test answered a narrower question than it was built for: rejection works
      (2 false additions removed, the one find kept), and detection is the limit. That agrees with
      AD-16's premise, and the two tracks now point the same way.
17. **engine (owner rule, 2026-10-17):** (a) the framework contract today says a single task may
    run in the main conversation and multi-task requests go to subagents ("Several tasks in one
    session"). The owner wants the main conversation to always be a coordinator managing ultracode
    workflows, with every task, even a lone one, farmed out to a subagent, so the contract's rule
    should change to that default. (b) the clean-close procedure today waits on the owner before a
    session closes. The owner wants a session to close itself (`context-engine session close`, the
    clean-close procedure) as soon as every task the owner named is done, without asking first.
    Suggest the engine record the named task set at intake, so "all mentioned tasks done" is
    mechanically checkable rather than left to the session's own judgement.
18. **engine: `banner set` accepts a banner that lint then rejects, and `commit` does not lint.**
    - **What happened at close.** The new banner was set and committed (`667bb19`). The close-docs
      commit `4c8e4f3` then went in with lint red, because `context-engine commit` runs no gate.
      Lint found two separate faults in the generated `HANDOFF.md`:
      - G-D8: a line opening with the session key reads as a stacked banner.
      - G-D1: two lines over 120 characters.
    - **The repair.** It took three more `banner set` rounds (`7106276`, `360db88`, `3bc4051`)
      before lint was clean.
    - **The fix.** `banner set` should run the same G-D1 and G-D8 checks on its input and refuse,
      as it already refuses a stale `--seen` hash. A `commit` that names any engine-rendered file
      could also lint first.
    - **Process lesson:** run lint after every engine write that renders a file, not only before
      code commits.

Items 19-36 were added on 2026-10-21 from the gap audit (see the Addendum). They are ordered by
severity, not by date.

19. **process: session 2026-10-17a died when the laptop ran out of commit memory, and the cause
    was not found.** This item transcribes the forensic note, `.scratch/ad16-r1/forensics.md`,
    which is gitignored, so this item is its only tracked copy.
    - **What happened.** At about 20:39 on 2026-10-17 the laptop had committed 129.5 GB of a
      130.7 GB limit, and about 2,550 nested `bash.exe` processes "from another command" held
      104 GB (`docs/results/2026-10-17-ad16-bout-verifier.md` § 5-9). AD-22's file records
      130.5 of 130.7 GB at the same minute (`docs/results/2026-10-17-ad22-distance-probe.md` § 7).
      The ledger dates the session's death to about 20:55.
    - **The casualties.** Every detached run then going died of `MemoryError`:
      - the precision rung's two feature workers (the rung was filed as AD-24 on 2026-10-19;
        scenes 844, 845 and 850 were already cached whole);
      - AD-20's run at its 26th scene, inside `hidden.refine_v`
        (`docs/results/2026-10-17-ad20-candidate-places.md` § 7);
      - AD-22's two probes (the clean rerun at 9 of 24 scenes, the edge set at 21 of 23).

      All of them resumed by scene on 2026-10-19 on unchanged code, checked by md5 or by "no
      script changed since". The fork failures also left `bash.exe.stackdump`,
      `grep.exe.stackdump` and `ps.exe.stackdump` in the repo root. They were untracked and were
      deleted on 2026-10-19.
    - **The forensics (read-only; the note's mtime is 2026-10-19 10:36).** The window is
      19:18-20:55 (+08). The scan covered the agents of workflow `wf_e77db043-981`, the top-level
      transcript and other repos' transcripts for the same window.
      - **Result: no self-calling construct was found, so the cause is NOT proven.**
      - `~/.bashrc` holds only a `docker` function, which calls a `.cmd`, not itself.
      - The workflow's subagents shared one shell snapshot. It was stale, dated 10-15 07:28. Its
        functions are git completion, `docker`, `rg` and `pkill`, and none of them recurses.
      - No command in the window recursed. Every `until`/`while` loop came later and
        terminated, and there was no `pkill`, no Monitor and no `nohup`.
    - **Most likely trigger (confidence about 25%; the only evidence is timing).** At 19:17:36 an
      AD-22 stream agent ran one Bash command of the shape
      `D=... && P=...python.exe && ... && rm -f ... && ( $P scripts/ad22_ladder.py ... pin912 ...;
      echo "pin912 rc=$?" >> stage.txt ) & echo pid1=$! ; ( $P scripts/ad22_ladder.py
      --truth-only ... ) & echo pid2=$!`. That matches the chain's start (about 19:18).
      - **The hypothesis:** `A && B && ( C ) &` backgrounds the whole `&&` list as a Cygwin
        subshell, with `set -o monitor` from the snapshot. That leaves two long-lived native
        python children under forked bash subshells, which inherit the `bash -c source snapshot`
        command line.
      - **Why it is not enough:** that gives 2-4 bash processes, not 2,550. A further runaway
        fork is needed, and no transcript shows one.
      - **Ruled out:**
        - Two `fetch_speech.py` launches with `run_in_background` were clean (only urllib and
          tarfile).
        - The later AD-22 chain scripts were linear, and their stage files show they finished
          normally.
        - The stackdumps (ps 20:42, grep 20:48, bash 21:36, empty) are victims of fork failure,
          not causes.
    - **The gap the note records:** nobody recorded which process was the chain's root. It could
      have been another Claude session's Bash tool, since the snapshot is shared. "Next time
      capture `ps -ef` ancestry of the deepest bash and the root's parent before killing."
    - **The one-line rule it proposes**, verbatim: "Never background (`&`) an `&&` chain or
      subshell from the Bash tool; launch long jobs with run_in_background on a single script
      file, and cap runaway forks with `ulimit -u 200` in that script."
    - **What changed afterwards.** The ledger says "rule added to agent prompts" (2026-10-19a
      summary). At least one of the 2026-10-19 round's agents logged free virtual memory and a
      `bash` process count before running (`.scratch/ad16-r1/ad7-fix2.md`: "FreeVirtualMemory
      KB: 49279992", "bash: 31").
    - **Engine angle.** The laptop is shared, so one session's runaway can kill another's runs and
      the session itself. A dead session leaves no pause and no batons. What brought it back is
      outside the engine: workflow journals (item 23), resumable runs, and an owner who could say
      the session was gone.
20. **process: the crash's rule has no tracked home.** Item 19's one-line rule exists in the
    gitignored forensic note and in the 2026-10-19 round's workflow prompts. It is not in
    CLAUDE.md or in the global `~/.claude/CLAUDE.md` (both read 2026-10-21). CLAUDE.md has
    117 bytes left under G-D1's cap (item 10's update), so it cannot take the rule as written. A
    rule whose trigger is a shell idiom any agent may reach for has to be where every agent reads
    it. Until it moves, item 19 is the only tracked copy.
21. **process: 2026-10-14d died too, three days earlier, from a laptop restart.** The laptop
    restarted mid-workflow. The ledger's abandon line says its work was "on branches ultra/AD-5,
    ultra/AD-1, ultra/AD-2 (uncommitted, worktree wf_85ee98e5-d4c-4), ultra/AD-3 and in
    .scratch/ultra-14d/". 2026-10-15a abandoned it at the owner's word ("The prev session is not
    coming back, either abandon it or resume it") and finished its four-task round. That makes two
    session deaths between 2026-10-14 and 2026-10-17, and neither was closed or paused. This one
    came before this review began, so it is entered here, not in the Timeline.
22. **engine: a dead session's uncommitted op lines go into the next session's first commit.**
    2026-10-17a's four op lines (`session.start`, two `ask.raised` lines, one on ASK-11 and one
    on the ledger entry, and the AD-16 comment holding the owner's delegation words) were never
    committed. 2026-10-19a's first `context-engine commit`, `a24d18d` ("engine: new DEC-80,
    ask.answer ASK-11, session.start 2026-10-19a"), took them along. Its message disclosed it:
    "Also carries 4 op log lines left uncommitted by session 2026-10-17a, with the files they
    name." That worked here, because the other session was dead.
    - **The risk.** `commit` takes "the op lines still uncommitted", whoever wrote them. With two
      live sessions on one tree, one session's commit would carry the other's op lines.
    - **The cost of the gap.** The owner's delegation words existed only in the working tree from
      2026-10-17 19:07 to 2026-10-19 10:33.
    - **The fix.** `commit` could take only the calling session's op lines by default, and name
      any it leaves behind.
23. **engine (good): the dead session's round was recovered from its workflow journals.**
    2026-10-19a's close lists as read "workflow journals wf_e77db043-981 / wf_118c4497-19e /
    wf_044b4307-861". DEC-80 says it was "Ruled by fable ... (session 2026-10-17a, workflow
    wf_e77db043-981; transcribed by the coordinator in session 2026-10-19a)". The round resumed
    as `wf_118c4497-19e` (AD-16 log, 2026-10-19a). The journals outlived the session, and nothing
    in the engine did that work.
    - **A date gap:** DEC-80's `decided:` is 2026-10-19, the transcription date. The ruling was
      made in 2026-10-17a. The record has no field that holds both dates.
24. **engine: a decision taken on the owner's delegation is stamped as the owner's, and agent
    text was frozen as owner words.**
    - **The stamp.** DEC-80, DEC-81 and DEC-82 all carry `actor: owner`, and each body says
      "Ruled by fable on the owner's delegation". No field records who ruled under a delegation.
    - **DEC-80's body.** `ask answer` wrapped its whole answer text in the owner-quote italics.
      The wrapper opens at `*"> (owner, 2026-10-17: ...` and closes at
      `nothing here was written to the board."*`. So fable's entire ruling sits inside what
      reads as the owner's words. It includes a line meant for the coordinator, "The DEC below
      is proposed for the coordinator to record after first-hand verification".
    - **Why it matters.** The body is stamped (`body_sha`) and append-only, and lint passes it.
    - **The fix.** `ask answer` could take the owner's words and the ruling text as separate
      inputs, with a `ruled_by` (or `delegated_to`) field. A decision then shows whose judgement
      it carries.
25. **process: the auto-close rule (item 17) did not cover the dead session.** 2026-10-19a closed
    itself as soon as its tasks were done (`bb0892b`, 20:10:16). 2026-10-17a was still listed as
    open, and the owner had to ask: "Is the stuff from that session done? Can you close that
    session?" (ledger, 2026-10-17a entry). The hand-abandon landed 35 minutes after the close
    (`5c61449`, 20:45:38).
    - **The fix.** The clean-close procedure could include "abandon or hand over every other open
      session you can show is dead", with orient's open-session list (item 1) as the input. The
      named-task check item 17 suggests would not see this, because the owner never named it as a
      task.
26. **process: the first push since the cutover is recorded nowhere.** All facts below were
    checked on 2026-10-21.
    - **The push.** `.scratch/gate/push.log` (mtime 2026-10-20 19:14:16) holds "branch 'main' set
      up to track 'origin/main'" and `444efcc..5c61449  main -> main`. That is 97 commits, the
      first push since `444efcc` (committed 2026-10-13). HEAD and `origin/main` are both `5c61449`.
    - **No session.** `docs/ledger/ops.jsonl` has no op between 2026-10-19T20:10:15 and
      2026-10-21T07:56:58. The newest close's ledger entry still says "Nothing pushed."
    - **The gate did run first.** This corrects the audit. `.scratch/gate/g1.log` (19:03:20)
      ends "all documents extracted cleanly", `g2.log` (19:14:00) "732 passed, 10 warnings in
      638.15s", and `g3.log` (19:14:03) "lint: clean". `rc.txt` was not rewritten (still dated
      2026-10-19 13:22), so the run did not go through `.scratch/gate/run.sh`.
    - **No CI watcher was owed.** The repo has no `.github/` directory, so a push starts no runs.
    - **What is missing.** The gate-before-push rule held, but its only receipt is in gitignored
      `.scratch/`, and HANDOFF and the ledger now say something false. Orient could compare HEAD
      with its upstream and report the last push. A `push` op that can be written with no session
      open would give a push made outside a session somewhere to be recorded.
27. **engine: `banner set` and `session close` leave the rest of HANDOFF.md stale, and lint does
    not see it.** As found on 2026-10-21:
    - **Inside the banner.** Line 24 reads "**Next (owner): AD-18 (the voice tier)**". Line 32 is
      also inside the banner and reads "**Next session (owner): AD-7, then AD-18.**". It was
      carried over unchanged from 2026-10-16b's banner by `9f7a5a7`, and AD-7 has been done since
      DEC-81.
    - **Seeds.** Line 67 says "Other fresh sets start at 1001", and line 85 (§ Now, item 3) says
      "Other fresh sets start at 892". Line 83 still calls 772-795 plus 820-843 "reserved", and
      line 65 says they are SPENT.
    - **§ Now, item 1** still reads "AD-7 next ... Raise **ASK-10** ... at session start". ASK-10
      was answered as DEC-77, and AD-7 is closed.
    - **The cause.** § Now has not changed since `50e10c2` (2026-10-16, `banner.set 2026-10-15b`),
      through two closes. `banner set` replaces only the text it is handed, and the close
      procedure does not make the session reread the rest.
    - **The fix.** Lint could flag a task id that HANDOFF calls "next" when the board has it
      closed, and an ASK id it says to raise when it is answered. The close procedure could ask
      for § Now in the same step as the banner.
28. **engine: the owner's next task is blocked on a parked task, and nothing flags it.** As found
    on 2026-10-21:
    - **The conflict.** The banner says "Next (owner): AD-18". `task list` has AD-3 as the only
      NOW item (set by the owner on 2026-10-15) and AD-18 at LATER with `deps: AD-7, AD-21`.
    - **The blocker.** AD-7 is closed, and AD-21 is SOMEDAY: DEC-80's stop clause parked it
      (DEC-80, 2026-10-19 amendment). DEC-80 itself had ruled "AD-18's dep on AD-21 stays", before
      the stop clause fired.
    - **The fix.** Lint or orient could warn when an open task depends on a SOMEDAY task, and when
      the banner's "next" is not the board's NOW.
29. **process: a sabotage run edited a file that a running job then imported.**
    - **2026-10-17 (AD-22).** At 19:51 "the first clean run imported `ad22_distance_probe.py`
      while a sabotage check had it temporarily rewritten (its `full` lags negated)". The run was
      discarded and relaunched. "Rule kept from then on: sabotage only with no run starting"
      (`docs/results/2026-10-17-ad22-distance-probe.md` § 7).
    - **AD-20.** AD-20's first sabotage pass edited `places.py` in place and restored it by md5.
      Its sweep then moved to a tracked runner that edits in memory, `vetting/places/sabotage.py`:
      13 of 13 red, 2026-10-19 (`docs/results/2026-10-17-ad20-candidate-places.md` § 6).
    - **An earlier case (2026-10-14d).** AD-5's first sabotage "ran in the live worktree and was
      stopped (the running lean jobs had imported their code before it started; TaskStop left S1
      applied to `adhoc_sep/align.py`, restored by hand at once)". Source: the gitignored
      `.scratch/ultra-14d/AD-5/build.md` § 5.
    - **The gap.** `docs/runbooks/sabotage.md` § Traps says to sabotage "where no other session can
      commit the broken file: a worktree or a scratch copy". A worktree does not protect the
      session's own running jobs, which import from that same tree. The runbook could add "never
      edit a file a running job may import; mutate in memory or in a copy",
      with `vetting/places/sabotage.py` as the pattern.
30. **process: the worktree-isolated round (2026-10-14d/15a) had its own frictions, and this file
    never compared the two modes.** Before this review, the 2026-10-14d round ran each task in
    its own git worktree. 2026-10-16b onward used the shared tree. The friction below is from the
    gitignored build logs in `.scratch/ultra-14d/*/build.md` and the audit in `.scratch/audit-15a/`,
    transcribed here.
    - **Stale bases.** Every worktree was created at `444efcc`, "16 commits behind main" (it was
      `origin/main`, the last push). Each branch was reset or rebased onto main `5cb11b7` before
      any edit.
    - **Gitignored inputs are missing in a worktree.**
      - `extract_text.py --check` exits 1, "nothing audited" (AD-3).
      - Full pytest skipped 73 tests (AD-1: 303 passed, 39 min) or 77 (AD-3: 307 passed).
      - AD-5 pointed `FAST_ROOT` and `ADHOC_VAD_MODELS` back at the main tree (387 passed,
        41 min).
      - An AD-1 run crashed on scene 211 for want of `ADHOC_VAD_MODELS`.
      - AD-3 rendered from the main tree, because `data/noise` is only there.
    - **Reports had to be copied out.** "The Write tool is confined to the worktree" (AD-5;
      AD-3: "the harness refuses writes into the main tree except this report"). So each report
      was written in the worktree's `.scratch/` and copied to the main tree after every append
      (AD-2: by `.scratch/ad2/sync.py`). After the restart the worktree copy was "no longer
      synced".
    - **Four more scratch areas to sweep.** Each worktree's `.scratch/` needed its own audit. One
      of the four (wf-5, AD-3's ref-mic probes) was first left UNCLEAR as "the highest-risk
      incomplete item". It was finished later with no salvage found
      (`.scratch/audit-15a/wf5-AD-3.md`). `docs/facts.md` records that the worktrees' probe
      folders were "audited (no salvage left untracked) and recycled". No worktree or `ultra/*`
      branch is left (2026-10-21).
    - **The comparison.** The shared tree avoids all of the above, but it brings item 29's race
      and the concurrent-session hazards. Neither mode is free, and the choice was never written
      down.
31. **engine: a batch of linked tasks cited each other's ids before the ids existed.** 2026-10-16a
    wrote AD-16 to AD-23 in one planning session, and the bodies are append-only. AD-17's log:
    "Id references in the body were written before the ids landed: 'the voice tier (AD-23)'
    means AD-18." AD-18's log: "'the AD-17 metric' means AD-19's (rung 1); 'AD-20's model' means
    AD-21 (the joint model)." The only fix available was a comment. This is like item 2: lint
    does not check what a cross-reference says about the record it names.
    - **The fix.** A batch `task new` that takes symbolic names and resolves them to ids at write
      time, or an id reserve step before the bodies are written.
32. **process: agents draft records with a literal `DEC-<NEW>` placeholder.** Only the
    coordinator writes a decision, so only the coordinator learns its id. The AD-7 fix agent put
    two literal `DEC-<NEW>` placeholders into CLAUDE.md, with the instruction "Substitute the real
    DEC id after the decision is written, before committing"
    (`.scratch/ad16-r1/ad7-fix2.md`, Steps 1 and 4). It was substituted (CLAUDE.md line 190 now
    says DEC-81). AD-16's 2026-10-19a log entry, which is append-only, guesses instead: "DEC-82
    if numbered so". The guess held. Nothing mechanical stops a placeholder or a wrong guess from
    being committed.
    - **The fix.** `record reserve decision` (an id handed out before the body exists), or a lint
      check for `DEC-<NEW>`-style placeholders in tracked files.
33. **engine: the residual-risk register has never been created.** `register show` refuses: "no
    register at ...\docs\invariants.md. Remedy: the first `task close` that files a residual
    creates it" (2026-10-21). `docs/ledger/ops.jsonl` holds six task closes since the cutover
    (AD-5, AD-19, AD-17, AD-7, AD-20, AD-24), and none filed a residual. There were candidates:
    2026-10-16b's close lists "AD-17's 886 t4 S2 separation outlier (-187 dB) is unexplained",
    and DEC-82 records a host-confusion trap. Either `task close` never asks for a residual, or
    sessions skip the question, and the record cannot tell which.
34. **repo: charter.md and criteria.md are still the unfilled templates, a week after the
    cutover.** `docs/charter.md` still has G-1 as "*(the owner's words)*", and `docs/criteria.md`
    has a header row and nothing else. Both are unchanged since `7100077` (2026-10-14).
    `docs/stories/` holds only `.gitkeep`. Lint passes. The project's real goal is in
    `docs/project-brief.txt`, which the framework does not read. Orient or lint could report a
    template placeholder that has outlived the cutover, so the owner is asked once.
35. **engine: `CE_ACTOR` is free text, so the same agent signs under several names.** On
    2026-10-21, `docs/ledger/ops.jsonl` holds five actor strings: 128, 53, 52, 21 and 11 op lines.
    The session tier appears under three spellings (a full versioned id, a short version, and the
    bare tier name), so a query for one actor misses the rest. The 11-line actor is the cheapest
    tier, and it ran a whole top-level session, 2026-10-14c: it wrote DEC-69, answered ASK-9 and
    closed the session. That was before the owner's 2026-10-16 tier rule, and nothing records
    the choice. The engine could normalise the actor to a fixed vocabulary at `session start` and
    refuse a string it does not know.
36. **process: the newest close's receipt has no gate pass count, so the test baseline is
    stale.** `docs/runbooks/gate.md` § Test baselines: "the baseline is the `guards:` receipt of
    the newest `kind: close` entry in the ledger". 2026-10-19a's `guards:` lists sabotage results
    only, so the newest recorded baseline is still 2026-10-16b's "665 passed". The suite reached
    732 on 2026-10-19 (`2290cd4` to `a946896`; `8e9a2be`: "Docs only since the last full gate
    (732 passed)"). It passed 732 again on 2026-10-20 (`.scratch/gate/g2.log`, item 26).
    `session close` could refuse a `guards:` receipt that has no gate line.

## Close (2026-10-17)

- **Token use per round**, from the workflow usages this session actually ran: round 1 (AD-19's
  signature-identifiability build), 10 agents, 1.18M subagent tokens; the AD-13 pre-registration
  round, 4 agents, 0.69M; round 1b (AD-19's post-verdict diagnostic plus AD-22), 18 agents, 1.22M;
  the AD-13 fresh-test run, 17 agents, 0.92M; round 2 (AD-17 plus AD-23), 13 agents, 1.34M; the
  owner-rule round (this feedback file's item 17), 1 agent, 0.07M. The haiku CI/run-watch rounds
  cost about 47-53k tokens each, far below the sonnet build/review rounds; the one fable review run
  (AD-13's D-31 vetting) cost 213k, by far the most expensive single agent of the session -- in line
  with the standing rule that fable is for cases that are "really necessary", not a default tier.
- **Detached long runs survived their agent's turn every time, via `nohup ... & disown`.** Every
  background render/fit/score pipeline this session launched that way (AD-19's full run, AD-19's
  diagnostic, AD-22's ladder, AD-13's fresh test, AD-17's full run) was still running, or had
  finished cleanly with its `ALLDONE` line, when its launching agent's turn ended and a later
  agent or the coordinator came back to read `stage.txt`. None needed to be restarted.
  - **Update (2026-10-21): true of that session, but not of the next one.** Detached runs outlive
    their agent's turn, not the machine. At about 20:39 on 2026-10-17, while 2026-10-17a ran, the
    shared laptop hit its commit limit, and every detached run then going died of `MemoryError`:
    AD-24's two feature workers, AD-20 at its 26th scene, and AD-22's two probes (item 19). All
    of them were resumed by scene on 2026-10-19, on code checked unchanged. They were saved by
    being resumable, not by `nohup ... & disown`.
- **Where the record boundary made work wait:** every write to a stamped record went through the
  coordinator, not the task agents that produced the evidence for it -- DEC-78 (AD-16 continuing
  past AD-19's mixture KILL), DEC-79 (AD-13 parked), the AD-17/AD-19/AD-22/AD-23 task
  comments and closes, and this session's own close (banner, ledger, ask). A task agent that
  finished a run and wrote its results file still had to hand the verdict back up a level before
  anything got recorded; no task agent wrote a decision or closed a task directly.
- **The verdicts this session produced:** AD-19 KILL on the mixture (overridden to continue, by
  owner's word, DEC-78); AD-17 KILL by its own pre-registered bar (false bouts, not recall);
  AD-22's kill bar not clearly tripped on the realised far-talker distances; AD-13's DEC-77 fresh
  test FAIL on bars 2 and 3 (net +1, not the required +2; 1 short find, not 2), parking AD-13
  (DEC-79).
- **Review loops caught one real defect and three clean passes.** AD-13's Fable review found one
  blocking defect, B1 (a specification gap: no tracked callable and no tracked scoring path for
  rejection test (c)), fixed the same day before the pre-registered run. The sonnet reviews of
  AD-17, AD-19's diagnostic, AD-22, and AD-23 each returned no blocking finding -- consistent with
  those builds following an already-reviewed pattern (AD-17 and AD-19's diagnostic reused AD-19's
  harness shape; AD-22 and AD-23 reused tracked generator/ladder code) rather than evidence that
  sonnet review is systematically weaker here; nothing in this session sabotaged a sonnet-passed
  check to find out.

## Addendum (2026-10-21)

- **Where these entries came from.** The owner asked, on 2026-10-21, what was recorded about the
  framework but missing from this file (Owner's instructions above). A read-only gap audit read
  the ledger, HANDOFF.md, `docs/facts.md`, the decisions, the board, the results files, the git
  log, the auto-memory and `.scratch/`. On the owner's word, every finding it marked absent or
  partial went in here.
- **What was added.**
  - Four owner quotes, under Owner's instructions.
  - Four Timeline bullets (2026-10-17a, 2026-10-19a, the 2026-10-20 push, 2026-10-21a), and a
    dated update to the Timeline's hook note.
  - Observations 19-36.
  - Dated updates under items 3, 10 and 11 and under Close's second bullet. The older text is
    left as it was written.
- **Each source was re-checked before its entry was written.** Three of the audit's claims changed
  on re-checking:
  - The 2026-10-20 push did have a full gate first (item 26).
  - There were six engine task closes, not about ten (item 33).
  - The worktree audit the audit called incomplete was finished later (item 30).
- **Facts are as found on 2026-10-21**, and the measured numbers carry their own dates. For
  example, CLAUDE.md is 18883 of 19000 bytes and 327 of 330 lines (2026-10-21), and HEAD and
  `origin/main` are both `5c61449` (2026-10-21).
- **Two items are this file's transcriptions of gitignored notes.** Item 19 is from
  `.scratch/ad16-r1/forensics.md`, and item 30 is from `.scratch/ultra-14d/*/build.md` and
  `.scratch/audit-15a/`. A sweep of `.scratch/` can now treat those notes as SUPERSEDED by this
  file.
- **This file reports what is stale; it fixes none of it.** HANDOFF.md (item 27), the ledger's
  "Nothing pushed" (item 26), the board (item 28) and CLAUDE.md (item 20) were left untouched.
