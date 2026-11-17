# Engine feedback from the adopting repos, collated (2026-11-17)

FROZEN: the collation as of 2026-11-17 (engine 5d806f7), session 2026-11-17b; the follow-up is the records in § Filed.

Session 2026-11-17b. Owner, 2026-11-17: "Okay collate all the feedback, let's handle that now and then we can upgrade
those to 0.6 / The demo repo is a clone so the feedback might just be a duplicate". A read-only opus agent collated
(`.scratch/feedback-2026-11-17/collation.md`), a second opus agent verified it independently
(`.scratch/feedback-2026-11-17/verify.md`: 38 rows confirmed, 2 corrected, 0 refuted, 1 missed), and fable gave a
second opinion the owner invited (`.scratch/feedback-2026-11-17/fable.md`, summarised in the last section). The table
below is the collation with the verifier's corrections applied in place; a corrected row says so.

## Filed

Filed in session 2026-11-17b by the coordinator's calls:
- DEC-347 (PROVISIONAL, agent's call): a lint failure inside an append-only body exits through a per-record waiver,
  not grandfathering (F31's residual, F32).
- CE-238 (F31): G-D3 counts column-0 bold `**N. ...**` paragraphs and top-level ordered items as numbered sections.
- CE-239 (F32 and F31's residual 6): `record waive`, per record and per text (DEC-347).
- CE-240 (F33, folding F21, F35, F36, F41): ref-stamped Upgrade lines and a from-pin checklist in kit README § 4.
- CE-241: upgrade adhoc-microphone-array, then audio-workspace, to 0.6.
- CE-242 (F28, F40): `context-engine upgrade --dry-run`, specified from CE-241's field evidence.
- LATER: CE-243 (F16, the problem only), CE-244 (F17 with F29), CE-245 (F20), CE-246 (F24), CE-247 (F26).
- Comments: CE-208 (F4), CE-209 (F5, F6), CE-216 (F9), CE-210 (F10), CE-211 (F11), CE-213 (F14), CE-166 (F30 with
  F34), CE-222 (F22), CE-193 (this pick-up).
- Not filed: F25 and F27 stay ideas in this doc; F15 and F18 (PARTLY, their tasks closed) and F23, F37, F38 have no task
  this round.

## Sources

1. adhoc-microphone-array `docs/results/2026-11-14-ad112-engine-feedback.md`, 79 lines, 30 items (tag `AD112#n`),
   verified at engine 989982a. Engine commits since: 12; code changed only in e9eab4b (CE-237); 81b13aa (CE-40)
   touched `src/context_engine/REGISTER.md` only.
2. audio-workspace `docs/context-engine-feedback.md`, 188 lines, entries 1-13 (tag `aw#n`), last commit 380c0066
   (2026-11-11). CE-193's Log 2026-11-07e took entries 1-12; only aw13 is new, and AD112 items 7, 13 and 14 already
   carry it. audio-workspace-demo's copy (167 lines, CRLF): see § Demo-clone verdict.
3. adhoc-microphone-array since 2026-11-14 (tag `A+`): `docs/ledger/session-log.md` L1-172 (2026-11-14a..2026-11-17b,
   HEAD 477290a); the 13 tasks touched since (engine-related: the AD-112, AD-113 and AD-122 Logs).
   audio-workspace since 2026-11-11 (tag `aw+`): session-log L1-380 (2026-11-10f..2026-11-15b, HEAD 353491c0, 41
   commits ahead of origin, pin still 4f2cef2); 34 tasks and 81 commits since 2026-11-11 grepped for engine friction.
4. intervals (tag `IV`): session-log L1-100, upgrade commit 5b5c011, 24 task files since 2026-11-01 (IV-23 only
   engine-related). graph-reachability-zanzibar-index (tag `ZK`): session-log L1-100, upgrade commit ebf71d8, TK-301.
   No feedback file in either. `.scratch/ce-235/agent.md` here (tag `CE235`, the CE-235 upgrade agent's report).
5. Engine side: `docs/framework/RELEASE-NOTES.md`, kit README § 4 Upgrade (`src/context_engine/kit/README.md`), the
   frontmatter of every cited task.
6. Dry runs, read-only (`git status --short --ignored` identical before and after), engine HEAD `lint`:
   adhoc rc 1, 6 lines (G-W6 x1, G-D0 x2, G-D3 x3); audio-workspace rc 1, 141 lines (G-D3 x137, G-D0 x2, G-D8 x1,
   G-W6 x1); intervals and zanzibar `lint: clean`, rc 0 (the verifier's run). The default `gate_receipt` regex
   (config.py::GATE_RECEIPT) fails all five adopter receipts tried; it passes "gate not run (records only)".

## What was not read

- Claude transcripts of any repo (AD112 notes its own transcript scan was partial).
- Anything held only in another session's chat in audio-workspace (its tree was clean at read time).
- intervals and zanzibar: not every task since 2026-11-01 (318 zanzibar task files, mostly the CE-167 import);
  grepped for engine mentions and TK-301 read.
- The engine's MCP tools were not used.

## Items

Status: FIXED / FILED / PARTLY / NEW / BY-DESIGN, at engine 5d806f7. Severity: bug / friction / idea / low.
F1-F30 keep AD112's numbering; F31-F40 are new since that collation; F41 is the verifier's missed item.

| F | source | problem | sev | status at 5d806f7 | action | pre-upgrade? |
|---|---|---|---|---|---|---|
| F1 | AD112#1, aw1 "the mcp engine should be set up when setting up" | setup did not register the MCP server | idea | FIXED: CE-177 closed; bootstrap.py::next_steps | nothing | no |
| F2 | AD112#2, aw2 (owner) "a green gate is enough to ship" | green gate as the release decision | idea | FIXED: US-20, CE-194 closed | nothing | no |
| F3 | AD112#3, aw3 | `ask new` accepted empty Options/Recommendation | bug | FIXED: guards.py::ask_problems (CE-44/158/201); both pins lack it. CE-237's NEEDS CONTEXT form still requires a Context part | nothing (re-pin) | no |
| F4 | AD112#4, aw4 | no way to record an owner's partial answer | idea | FILED: CE-208 open LATER | comment | no |
| F5 | AD112#5, aw5 | owner words and ruling share one field | friction | FILED: CE-209 open LATER | comment | no |
| F6 | AD112#6, aw10 | every `ask answer` is its own commit | friction | FILED: CE-209 open LATER | comment | no |
| F7 | AD112#7, aw6, aw13 (2nd ask), A1 | close without banner leaves next gate red on G-W1 (aw 11-05..11-11, adhoc 5x) | friction | FIXED: CE-195 2165e3d (ledger.py::BANNER_KEPT, working.py::Engine._banner_kept). The first close after a re-pin must write the banner (working.py::Engine._banner_cut) | nothing (re-pin; see Hazards) | no |
| F8 | AD112#8, aw7 | "close eagerly" vs back-and-forth | friction | FIXED: CE-195, US-21, DEC-163, `session start --continues` | nothing | no |
| F9 | AD112#9, aw8, A6 | CE_ACTOR free text; one agent signs 6 ways | friction | PARTLY: CE-122 warns (working.py::Engine.actor_spellings); normalisation FILED CE-216 open LATER (DEC-324) | comment | no |
| F10 | AD112#10, aw9 | harness can refuse a write-capable agent's Write | friction | FILED: CE-210 open LATER | comment | no |
| F11 | AD112#11, aw11 | records-only commit waits ~90 min on a gate over others' dirty code (aw `[gate] require = "all"`) | bug | FILED: CE-211 open LATER | comment | no |
| F12 | AD112#12, aw12 (owner) | decide derivable/cheap questions; `ask decide` | idea | FIXED: US-24, CE-217/218 closed (DEC-325) | nothing | no |
| F13 | AD112#13, aw13 "five `banner set` calls"; aw+ 2026-11-15a "Re-wrapped a banner line over 120 chars that failed G-D1" | `banner set` writes a banner lint then refuses; each retry a commit. Recurred in aw 11-15 (pin 4f2cef2) | bug | FIXED: CE-63 1083e1d (working.py::Engine._banner_note calls working.py::Engine._refuse_prose); in adhoc's pin 9f0e8ca, not in aw's 4f2cef2 | nothing (aw re-pin) | no |
| F14 | AD112#14 (aw13 residual) | `_refuse_prose` compares failure multisets; a file already over a cap accepts more over-cap text | low | FILED: residual INV-60; twin CE-213 open LATER | comment | no |
| F15 | AD112#15, A2 | closing NOW leaves G-W5 red; promote is a 2nd step | friction | PARTLY: CE-36/CE-191 warn (working.py::Engine._now_short); `task close --promote` NEW, unfiled. A flag must take an explicit caller-named id, never pick one (CE-36's risk row; DEC-162) | none filed this round (fable: can wait) | no |
| F16 | AD112#16, A3 "NEXT already holds 5 of 5" | asks default to NEXT and share the tier cap with work | friction | NEW (cli.py `ask new --pri` default NEXT; working.py::Engine._cap_check counts every open board item); only DEC-100 filed | LATER task, worded as the problem (asks listed twice in orient and sharing NEXT's cap); no design pre-decided | no |
| F17 | AD112#17, A4 | `--brief` refusal gives only length; baton/pause titles cut mid-word at `[:100]` | low | NEW (working.py::Engine.baton_add; pause title likewise) | LATER task, merged with F29 | no |
| F18 | AD112#18, A5 "(and 2 more)" | schema refusal names only the first problem | friction | PARTLY: CE-187 defaults decision_status (working.py::Engine._born_status); store.py::Store._validate still raises `probs[0]` | none filed this round (fable: can wait) | no |
| F19 | AD112#19, A7 | ids cited before they exist, filled by hand | friction | FIXED: CE-105 ops.py::id_reserve, CE-119 guards.py::placeholders, CE-183 working.py::Engine._cites_known | nothing | no |
| F20 | AD112#20, A8 | a decision changes task briefs; nothing flags stale briefs | idea | NEW (nearest CE-115, HANDOFF only, closed) | LATER task | no |
| F21 | AD112#21, A9 (43 min-3.5 h gates; A+ 2026-11-15a pytest 2663.90 s) | the scoped gate `[gate]` is never a step or nudge for an adopter: not in init's next steps nor the upgrade steps (the kit contract and `context.toml.template` mention it conditionally) | friction, the costliest item by hours | PARTLY: built (CE-78, CE-181); discovery gap NEW (bootstrap.py::next_steps; kit README § 4 has no `[gate]` line) | fold into F33's task; write this line first | yes (doc line; AD-113 is when adhoc would add `[gate]`) |
| F22 | AD112#22, A10 (7 empty watchers); A+ 2026-11-17a "Pushed to origin/main (no CI on this repo)" | push procedure assumes CI | friction | PARTLY: procedures.md "Without CI" row (CE-68); fresh-clone skips FILED CE-222; "record no CI once, skip the watcher" NEW | comment on CE-222 | no |
| F23 | AD112#23, A11 | banner over orient's cap found by eye; hand-edited CLAUDE.md width caught only at next gate | friction | PARTLY: CE-76, CE-195, CE-231 (guards.py::cap_warnings, guards.py::headroom); a plain `git commit -o` of a hand edit is unchecked, NEW | nothing now (a pre-commit hook is a separate design call) | no |
| F24 | AD112#24, A12 | init's `.claude/.gitignore` lacks `worktrees/` | friction | NEW (bootstrap.py::_ensure_ignore writes `settings.local.json` only) | LATER task | no (AD-113 adds it by hand) |
| F25 | AD112#25, A13 | `hk expire_batons` turns owner-decision batons into LATER tasks with cut titles | friction | NEW (working.py::Engine._hk_expire has no owner-decision branch; DEC-68 keeps housekeeping free of judgement) | idea only, no task; the title cut goes with F17 | no |
| F26 | AD112#26, A14 | C0 control bytes in tracked docs pass lint | idea | NEW (no C0 check in guards.py, okf.py, store.py) | LATER task | no |
| F27 | AD112#27, A15 | receipts accept `read: none`; "Still owed" lines need no board id | idea | NEW (working.py::Engine.session_close refuses only an empty receipt) | idea only, no task | no |
| F28 | AD112#28, A16 | no `context-engine upgrade`; upgrade is by hand | idea | NEW (no `upgrade` parser in cli.py) | LATER task, specified from the two upgrades' field evidence (with F40) | no |
| F29 | AD112#29 | working.py::Engine._cap_check remedy says `promote <id> LATER`; the command is `task promote` | bug (low) | NEW | merged into F17's task | no |
| F30 | AD112#30, A+ 2026-11-17b "pytest not run (no code change)" | default gate_receipt refuses adhoc's records-only receipts after re-pin | friction | FILED: CE-166 open LATER (an adopter step on the engine board). Same engine behaviour as F34 (CE-192 default, DEC-162): merged with F34 on CE-166 | comment on CE-166 (with F34) | no |
| F31 | dry lint, audio-workspace: 137 x "G-D3 ...: `D-142 § 5's encoder-delay and` names no heading of D-142" (117 in docs/decisions/, 20 in tasks/) | **(corrected by verifier: the fix's scope.)** G-D3's `<id> § <n>` check (guards.py::cite_problems via guards.py::_headings and guards.py::_cites_heading) reads only markdown headings. Of the 137: **120** cite a `**N. ...**` bold paragraph (D-142 L251 `**5. TWO SILENT-WRONGNESS TRAPS ...**`); **11** cite a top-level numbered list item `N. **...**` (D-296, D-110 x5, D-273 and others); **6** cite a number the target does not have (D-152 § 5.3/5.6 x3, naming a README quoted inside D-152; D-284 § 2 and § 3; D-419 § 2, a body of only `## Amendments`), all six in append-only bodies (D-153 x3, D-285, D-418, D-290). The 20 in tasks/ are editable; the 117 in decisions are not | bug | NEW | NOW task: bold paragraphs and top-level ordered items count as sections (clears 131 of 137); the 6 true mis-citations stay red and go through F32's waiver | yes (aw's upgrade lint is red with no legal fix) |
| F32 | dry lint, adhoc: "G-D3 docs/decisions/DEC-93-...: line 16: names S-3, which is no record" (DEC-17 L19, DEC-93 L16, L21) | adhoc's story prefix is one letter (`S`), so the formula `(M-4)(S-3) >= 6` reads as citations of S-3/S-2 (guards.py::id_series). The bodies are append-only and `record correct` only inserts. Superseding the decisions or `[guards] off` G-D3 would clear it; neither is acceptable | bug | NEW (INV-10 is about prefix collisions outside record dirs, not prose arithmetic) | the per-record waiver decision and its task (also takes F31's 6) | yes (adhoc's upgrade lint is red with no legal fix) |
| F33 | CE235 "zanzibar closed fae13a2 (banner cut to durable lines: the 0.6 engine refused the close otherwise)"; ZK 2026-11-16a | **(corrected by verifier: three 0.5 sections, not two.)** The first close after a re-pin is refused until the banner is cut. The step is in RELEASE-NOTES under "0.5, from 2026-10-30", though CE-195 landed 2026-11-06 (2165e3d): a 0.5 pin from 2026-11-01 reads that section as applied, and kit README § 4 does not list it. RELEASE-NOTES has three 0.5 sections (from 2026-10-30, 2026-10-23, 2026-10-11 to 2026-10-23); adhoc's pin 9f0e8ca (2026-10-22) and aw's 4f2cef2 (2026-10-19) fall in the third, so they cross all three plus 0.6. Every `**Upgrade:**` line is in 0.6 or the from-2026-10-30 section, so no step is lost | friction | PARTLY: the note exists and the refusal names its remedy; notes are keyed by framework version and section date, not by the ref each line landed at; kit README § 4 lacks the banner, gate_receipt, G-I4/G-D3, `[gate]` and decision_index steps | NEXT task: stamp each Upgrade line with its landing ref; a from-pin checklist in kit README § 4 (folds F21, F35, F36, F41) | yes (both pins cross all three 0.5 sections and 0.6) |
| F34 | dry lint, audio-workspace: "G-W6 ... the newest close (2026-11-15b): the `guards` receipt has no gate result"; aw `[gate] command` = tsc + lint (prints no count) | **(corrected by verifier: the remedy.)** After re-pin aw's lint is red on its newest close and every later `session close` is refused until gate_receipt is set. A pattern on "engine gate green" (11 older closes) does not clear it: 2026-11-15b says "gate + node suite re-run first-hand before each of 6 commits". Set `[working] gate_receipt = ''` or a pattern that also matches the 15b wording. Same behaviour as F30 | friction | BY-DESIGN: CE-192, DEC-162 (RELEASE-NOTES names the remedy) | nothing in the engine; merged into F30's comment on CE-166; aw upgrade step (Hazards) | no |
| F35 | IV 5b5c011 "`decision accept --owners` found no owner decision PROVISIONAL" | kit README § 4 says run `decision accept --owners` once; with nothing to accept it is a refusal (working.py::Engine.decision_accept) | low | NEW | fold into F33: § 4 says that refusal is a pass | no |
| F36 | IV/ZK 2026-11-16a "Old engine env kept at .context-engine/env-309641b (gitignored) for the owner to delete"; adhoc AD-113 trap "keep the old env recoverable (rename, not delete)" | kit README § 4 step 1 says delete the env, then rebuild; adopters rename it and leave a dir for the owner | low | NEW | fold into F33: § 4 says rename to `env-<oldref>`, delete once lint and gate are green | no |
| F37 | CE235 "HANDOFF change stales t2c tiles -> rerunning all ten phases"; ZK 2026-11-16a | zanzibar's own `scripts/gate_status.py` keeps HANDOFF.md in its code scope, so the banner cut forced a full ten-phase rerun | low | BY-DESIGN / repo-side (kit README § 5 tells a CI to treat prose as prose) | nothing (note to zanzibar) | no |
| F38 | ZK TK-301 trap "The pinned ref is written in two places once this lands (CLAUDE.md and gate.yml)" | an engine upgrade must move the pin in CLAUDE.md and CI | low | NEW (repo-side; no engine check compares a CI pin) | nothing (TK-301 owns it) | no |
| F39 | ZK 2026-11-04a "record new does not lint before its commit" | `record new` committed a body G-D3 fails | bug | FIXED: CE-183 4793c9f (working.py::Engine._cites_known), in 989982a; zanzibar is on 989982a | nothing | no |
| F40 | dry lint, adhoc: 2 G-D0 lines, no ACCEPTED-enum line | G-D0's ACCEPTED-enum check runs only once the kit block is current, so a pre-upgrade dry lint understates what the upgrade surfaces | low | BY-DESIGN (working.py::Engine._accepted_enum) | goes with F28 (an honest upgrade estimate); F33's checklist names the enum step | no |
| F41 | **(missed by the collation, found by verifier: M1.)** intervals and zanzibar context.toml `decision_index = "docs/decisions/index.md"`, both files still tracked; zanzibar's index lists DEC-13..15 under `## PROVISIONAL` while DEC-13 is ACCEPTED (pushed with fae13a2); adhoc and aw set the same key and hold the file | the 0.6 upgrades left the dead decision index in place, and zanzibar's now misstates three owner decisions on GitHub. The step is only in RELEASE-NOTES and in orient's deprecated-config notice (working.py::Engine.deprecated_config); kit README § 4 does not list it and lint is silent | friction (low) | FILED as accepted residual INV-95 (CE-185's residual); the gap in practice is NEW | fold into F33's checklist ("delete `[working] decision_index` and `git rm` the stored index"); owed in intervals and zanzibar beside env-309641b; adhoc and aw hazards | no (orient flags it; nothing breaks) |

Counts (41): FIXED 9 (F1, F2, F3, F7, F8, F12, F13, F19, F39); FILED 8 (F4, F5, F6, F10, F11, F14, F30, F41);
PARTLY 7 (F9, F15, F18, F21, F22, F23, F33); NEW 14 (F16, F17, F20, F24, F25, F26, F27, F28, F29, F31, F32, F35,
F36, F38); BY-DESIGN 3 (F34, F37, F40). Pre-upgrade: F31, F32, F33 (with F21, F35, F36, F41 folded into F33).

## Upgrade hazards

### adhoc-microphone-array (AD-113; pin 9f0e8ca, 2026-10-22, framework 0.5)

1. Add ACCEPTED to `[kinds.decision]` enums, then `decision accept --owners` once (a "no owner's decision is
   PROVISIONAL" refusal is a pass, F35). G-D0 names the enum only after the kit block is replaced (F40).
   CE-237's `--covered-by`/`--gap` rule does not touch the `--owners` sweep.
2. The first close must write the banner (`session close --banner-file ... --seen <hash>`, or `banner set` first);
   otherwise it is refused (F7, F33).
3. Records-only receipts: the newest close 2026-11-17b ("pytest not run (no code change)") already fails G-W6 under
   HEAD's default. Set `[working] gate_receipt` (CE-166, F30/F34) rather than phrasing receipts around the regex.
4. Add `worktrees/` to `.claude/.gitignore` (F24).
5. Consider a `[gate]` section: pytest runs 1449-2663 s per close (F21).
6. G-D3 fails DEC-17 L19 and DEC-93 L16, L21: the formula `(M-4)(S-3)` reads as story ids under the one-letter `S`
   prefix. Append-only bodies: needs the waiver (F32) in the engine first.
7. G-D0 x2 (framework line, kit block): the expected contract/bootloader replacement.
8. Remove `[working] decision_index` and `git rm` the stored index (F41).
9. The pin crosses CE-195, CE-63, CE-105/183, CE-187, CE-192, CE-237: read all three 0.5 sections of RELEASE-NOTES and
   all of 0.6, not just kit README § 4 (F33). AD-113 Log: owner 2026-11-17 "okay lemme go look at that"; AD-122,
   AD-123 and AD-96 wait on the upgrade.

### audio-workspace (pin 4f2cef2, 2026-10-19, framework 0.5; 41 commits ahead of origin)

1. G-D3 x137 section citations (F31): 131 clear once bold paragraphs and top-level ordered items count as sections;
   the 6 true mis-citations in append-only bodies need the waiver (F32); the 20 in tasks/ are editable.
2. G-W6 on the newest close 2026-11-15b (F34): set `[working] gate_receipt = ''` or a pattern that matches the 15b
   wording too; "engine gate green" alone leaves lint red until the next close.
3. G-D8 "a stacked banner" (HANDOFF.md): cleared by the required first-close banner cut (F7, F33).
4. ACCEPTED enum, `decision accept --owners`, contract + bootloader + runbooks, as adhoc; remove `decision_index` (F41).
5. CE-193 still owes aw's re-pin for entry 3 (ask_problems); entries 1-13 are all taken once this collation is carried.
   aw's `.gitignore` already ignores `.claude/worktrees/`: F24 does not bite here.
6. Same release-notes span as adhoc (F33).

### intervals and zanzibar (upgraded 2026-11-16, pin 989982a)

Both lint clean at engine HEAD. **(corrected by verifier: the push is not owed.)** Both were pushed on the owner's word
(CE-235 Log 2026-11-17a: intervals ed10d54, zanzibar fae13a2, CI green; both in sync with origin). Still owed by the
owner: delete `.context-engine/env-309641b` in each (deleting untracked files; F36), and the dead `decision_index`
key and stored index in each (F41; zanzibar's misstates DEC-13..15 on GitHub). Neither needs CE-237 urgently.

## Demo-clone verdict

audio-workspace-demo is not a separate clone: it is a worktree of audio-workspace on branch `demo/offline` (HEAD
0376ca5e, 2026-11-12; `git worktree list`), forked from main at 34523a4a, before 380c0066 added entry 13. Its feedback
file is lines 1-167 of main's, byte for byte apart from CRLF (`diff --strip-trailing-cr`), and lacks only entry 13. The
23 demo-only commits touch no ledger, task, HANDOFF or feedback file. Verdict: a strict subset; nothing new.

## Second opinion (fable, owner-invited)

Fable (read-only, engine 5d806f7) read the collation, the verification and the G-D3 code.

1. **F31 and F32 are one structural problem:** lint checks at rest over bodies the repo may not edit, and the engine
   offers no recorded way out. The write-time twins already concede it (guards.py::added_refs: "an old red is lint's,
   not this write's"), and every future body-reading guard will hit frozen text the same way. Decide the exit once,
   then fix the two.
2. **F31:** widen what guards.py::_headings calls a section: besides `#` headings, a column-0 line that is wholly bold
   and opens with a number, and a column-0 top-level ordered item, matched by number and text as
   guards.py::_cites_heading does today. Not indented items, not a number inside a prose line, not bold text that is
   not the whole line, and the existence test is not widened. Clears 131 of 137; the 6 true mis-citations stay red,
   correctly.
3. **F32, options weighed:** registered prefixes with word boundaries are already the case and do not help; a
   math-context heuristic special-cases one formula and would hide a real `(see S-3)`; a per-repo `[guards]
   allow_ids` list is one line of code but repo-wide and forever, so keep it only as an emergency fallback;
   grandfathering by body_sha or date hides exactly what the at-rest check exists to find (aw's 6 real mis-citations
   would vanish), its baseline is arbitrary, and it is `[guards] off` by stealth. **Recommended:** a waiver as an
   amendment, one op (`record waive <id> <guard> "<exact text>" --reason ...`), in the shape `corrected:` already
   uses; lint skips that text in that record only; never a whole guard, never text appended after the waiver, never
   hand-editable. A record write, so an agent may make it, flagged in the close digest. Every citation is then either
   resolvable or explicitly signed off.
4. **Order before the upgrades:** F31, then F32 with F31's residual 6, then the F33 docs (folding F21, F35, F36, F41)
   last so § 4 can name the waiver op. Stamp each `**Upgrade:**` line with its landing ref in a fixed form
   (`**Upgrade (at <sha>):**`) so F28 can parse it later. F21's `[gate]` line is the highest-value line: write it first.
   Then adhoc first as the rehearsal (6 lint lines, newer pin, F13 already in), then aw (141 lines, stacked banner,
   F13 missing, gate_receipt to set). Rename old envs, delete after green.
5. **Can wait** (LATER, after both upgrades): F15 (explicit id only), F16, F17 with F29, F18, F20, F22, F24, F26, F28.
   Merge F30 into F34 (one behaviour, two repos). Reject nothing outright; F25 and F27 stay ideas.
6. **F28 vs more docs:** both, docs first. The command is the better end state (pinned ref from `direct_url.json`,
   release-note steps since it, lint with remedies, orient's deprecated-config section), but it cannot be specified
   well before the two upgrades produce field evidence, and it needs the ref-stamped notes. File it NEXT right after
   the upgrades, with both upgrade Logs as its spec.
7. **Where the collation's judgement is off:** two narrow parser tasks hide the shared cause; F30 FILED vs F34
   BY-DESIGN is inconsistent, and phrasing receipts around a regex teaches the wrong habit; F16's proposed task bakes
   in a design (the better reason is that open asks are listed twice, in orient's questions and in NEXT's cap); F40
   undercuts the dry-lint method (one more argument for F28); F21 is ranked as friction with a one-line action though
   it costs the most hours; the intervals/zanzibar owed push was stale, and F41's dead `decision_index` belongs in
   § 4's checklist, not only in orient.
