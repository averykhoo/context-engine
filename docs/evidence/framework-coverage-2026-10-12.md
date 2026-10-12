# Framework coverage map, 2026-10-12 (CE-16, G7, US-9)

FROZEN 2026-10-12b. The board moves on after this; the map does not. CE-30 would keep a
newer map honest mechanically.

**Question (G7, US-9):** the charter is now the whole framework (DEC-10), but the board was
scoped to the record engine. Is every FRAMEWORK.md component, ritual and guard owned by a board
item, deliberately prose-only, or deliberately deferred?

**Method.** Read `docs/framework/FRAMEWORK.md` at `40eada6` (1676 lines, 105960 B) for §2 (the 23
components), §5.6 and §6.1 to §6.13 (the rituals), §8.0 and §8.1 to §8.5 (the guards), plus §3,
§7, §9.4 and §11 for context. Every guard id was grepped in `src/` and `tests/`; every symbol
cited as built below was grepped first-hand, and the commit that introduced it was read with
`git log -S`. Every CE id cited was read with `task show`. "Built" means code in `src/` plus a
test that fails without it. The census was done in one session by section-targeted reads, not
by delegated agents (the build agent had no agent tool); it is not a full-text audit of each
section's every sentence.

**Classes.** `EXISTING CE-n` (an open item owns it, or a closed item built it: marked *built*);
`NEW CE-n` (filed by this map); `PROSE-ONLY` (a rule that needs no tool, with where it lives);
`DEFERRED` (with the reason and what un-defers it). Each row has exactly one class; where work
is split, the reason names the other homes.

## Components (FRAMEWORK §2)

| # | Component | § | Class | Home | Reason |
|---|---|---|---|---|---|
| 1 | Charter | §3.1 | NEW CE-25 | `docs/charter.md` (hand-written) | Goals are prose no tool reads; G-I1 needs goal ids. |
| 2 | Stories | §3.2 | EXISTING CE-8 (built) | `working.py::Engine.record_new`, `Engine.amend`, `Engine.stamp`; `[kinds.story]`; `tests/test_working.py::test_record_stamp_is_all_or_nothing_and_amend_appends` | Story kind, verbatim body, `body_sha`; story guards G-I1/G-I2 are CE-25. |
| 3 | Criteria (the spec) | §3.3 | NEW CE-25 | `docs/criteria.md` (hand-written); `pyproject.toml` `criterion` marker | No criteria kind and no status or ref checks (G-T1, G-T2, G-T6). |
| 4 | Law / NFRs | §2, §11.2 | DEFERRED | none | Optional; §11.2 trigger "cross-cutting NFRs or data law" not hit. Un-defer: the first such law, then a law doc with its invariant to test map. |
| 5 | Deviation register | §3.5 | DEFERRED | none | §11.2 trigger "the code deliberately departs from the spec" not hit; no `deviates` criterion exists. Un-defer: the first deviation; it brings G-T7. |
| 6 | Contract | §2 | PROSE-ONLY | `CLAUDE.md` | Hand-written by design (changes by promotion only). Its checks are G-D0 (CE-21) and G-D1 caps (CE-14). |
| 7 | Routing map | §2, §11.4 | EXISTING CE-8 (built) | `context.toml` `[[routes]]`; `working.py::Engine.lint_routes` | `routes` prints it; G-R1 guards it. |
| 8 | Invariants (residual-risk register) | §7.4 | EXISTING CE-23 | not built yet | CE-23 builds the register file and the design-review section. |
| 9 | Runbooks | §7.5 | NEW CE-26 | `docs/runbooks/manual-mode.md` only | Gate, sabotage, fan-out, release and baseline runbooks named in §7.5 do not exist. Ritual order is CE-24. |
| 10 | Orientation note | §5.1 | EXISTING CE-2 (built) | `ledger.py::Banner`; `working.py::Engine.banner_set` | Banner stamped, written only if unchanged since read; G-D8 is CE-14. |
| 11 | Tasks and the board | §5.2, §5.3 | EXISTING CE-2 (built) | `working.py::Engine` task and ask operations; `BOARD_OWNED` | Questions are board rows; caps G-W5. |
| 12 | Batons and pause records | §5.4 | EXISTING CE-2 (built) | `working.py::Engine.expire_batons`; `[kinds.baton]`, `[kinds.pause]` | Expiry into tasks is built (G-W3); other housekeeping is CE-6. |
| 13 | Unverified hazards | §7.4 | NEW CE-29 | none | No declared home, route or kind. |
| 14 | Decisions | §6.5 | EXISTING CE-5 | `[kinds.decision]`; record new / amend / stamp built in CE-8 | Supersede, why(), generated index and importer are CE-5. |
| 15 | Session ledger | §7.1 | EXISTING CE-2 (built) | `ledger.py::Ledger`; `working.py::Engine.session_start`, `session_close`, `session_pause` | Rotation and `kind: abandoned` are not built (CE-6, per `working.py` module docstring). |
| 16 | Evidence and plan docs | §7.2 | NEW CE-27 | `docs/evidence/` (Evidence route) | Hand-written and routed; nothing freezes an ACTIVE-PLAN doc on close. |
| 17 | Archive | §7.3 | NEW CE-27 | none | No archive operation, ARCHIVED line or redirect table. |
| 18 | Tests and proofs | §2 | EXISTING CE-1 (built) | `pytest -q` gate; `criterion` marker in `pyproject.toml` | The gate exists; criterion claims are checked by G-T2 (CE-25). |
| 19 | Trace and existence guards | §8.2 | EXISTING CE-14 | see guards table | G-T3 is CE-14; the intent-chain ones are CE-25. |
| 20 | Doc and working-state guards | §8.3, §8.4 | EXISTING CE-14 | see guards table | Part built (CE-1, CE-2, CE-8); the rest is CE-14. |
| 21 | Verification state | §8.5 | EXISTING CE-17 | not built | Run ledger G-V1, tiles. |
| 22 | Scratch | §2 | PROSE-ONLY | global `CLAUDE.md` § `.scratch/`; optional `.scratch` route in `context.toml` | A throwaway area needs a rule (gitignored, evidence out the same hour), not a tool. |
| 23 | Memory | §2, §6.7 | NEW CE-29 | Claude Code auto-memory, outside the repo | No promotion or prune step exists. |

## Rituals (FRAMEWORK §5.6, §6.1 to §6.13)

| Ritual | § | Class | Home | Reason |
|---|---|---|---|---|
| Owner digest | §5.6 | NEW CE-28 | `working.py::Engine.session_close` (1 to 7 line summary, built) | The digest is built; the cross-repo question index and its nag are not. |
| Session start | §6.1 | EXISTING CE-2 (built) | `working.py::Engine.session_start`, `Engine.orient` | Built; the tier-0 SessionStart hook is CE-6, the ordered steps CE-24. |
| Intake | §6.2 | NEW CE-25 | `Engine.record_new`, `Engine.amend`, `ask answer` (step 1 built) | Steps 2 to 6 (goal link, criteria, census) need the intent chain. |
| Clean close | §6.3 | EXISTING CE-2 (built) | `Engine.session_close`, `Engine.banner_set`, `hk_expire_batons` | Built; the ordered steps and their by-hand section are CE-24. |
| Pause | §6.4 | EXISTING CE-2 (built) | `Engine.session_pause`; `pause open` / `pause resume` | Built; the pause commit lacks a `Session:` trailer (CE-22). |
| Decision recording | §6.5 | EXISTING CE-5 | `[kinds.decision]`; `store.py::ACTOR_RE` | Actor vocabulary is already schema-checked; links, supersede and index are CE-5. |
| Delegation and build rounds | §6.6 | NEW CE-26 | `CLAUDE.md` § Rules (DEC-16, DEC-17, DEC-18) | The delegation rules are written; the build-round protocol has no runbook. |
| Promotion and demotion | §6.7 | NEW CE-27 | none | The table is checked by nobody; archive and freeze have no operation. |
| Push and CI | §6.8 | EXISTING CE-10 | `CLAUDE.md` § Rituals step 6 (DEC-22); global `CLAUDE.md` § Git | The push rules and watcher are prose; CE-10 puts the gate in CI. |
| Bootstrap | §6.9 | EXISTING CE-15 | not built | CE-15's brief names bootstrap (§6.9) and adoption (§11). |
| Humans outside the rituals | §6.10 | EXISTING CE-12 | trailers: `CLAUDE.md` § Rules (DEC-22), CE-22 | Foreign-commit reconciliation (ledger `kind: foreign`, inbox check) is in CE-12's body, on CE-6's script. |
| Housekeeping | §6.11 | EXISTING CE-6 | `Engine.expire_batons` (only tier-0 operation built) | Tier 0 is CE-6, tier 1 CE-12. |
| Keeping FRAMEWORK current, AAR | §6.12 | PROSE-ONLY | `CLAUDE.md` § Rules (DEC-19, US-12) | Editing in place and archiving are judgement; CE-9 did the trim. The AAR is an open idea (US-12): it goes in the ledger `summary:` until designed. |
| Rollback and close | §6.13 | EXISTING CE-18 | not designed | US-13. |

## Guards (FRAMEWORK §8.0, §8.1 to §8.5)

| Guard | § | Class | Home | Reason |
|---|---|---|---|---|
| G-I1 | §8.1 | NEW CE-25 | none | Needs charter goal ids. |
| G-I2 | §8.1 | NEW CE-25 | `[kinds.story]` schema covers part | Story actor/date/status are schema keys; the `unconfirmed` actor rule is not checked. §11.1 minimum set. |
| G-T1 | §8.2 | NEW CE-25 | none | Needs criteria as data. §11.1 minimum set. |
| G-T2 | §8.2 | NEW CE-25 | `criterion` marker exists, unchecked | §11.1 minimum set. |
| G-T3 | §8.2 | EXISTING CE-14 | none | Existence check over normative prose. |
| G-T4 | §8.2 | DEFERRED | none | §11.2 trigger "the spec makes structural claims" not hit. Un-defer: the first pinned structural claim. |
| G-T5 | §8.2 | DEFERRED | none | Needs CE-14's lint frame and a large suite (§11.2). Un-defer: CE-14 lands; the hand sabotage rule (DEC-11) covers it until then. |
| G-T6 | §8.2 | NEW CE-25 | none | Needs criteria refs as data. |
| G-T7 | §8.2 | DEFERRED | none | Comes with the deviation register (component 5); un-defer with it. |
| G-D0 | §8.0 | EXISTING CE-21 | none | Contract `framework:` against the engine version. |
| G-D1 | §8.3 | EXISTING CE-14 | none | Caps with provenance. |
| G-D2 | §8.3 | EXISTING CE-14 | partial: `store.py::Store.ids_in_use`; `tests/test_store.py::test_ids_count_closed_and_legacy_records_and_are_never_reused` | Allocation never reuses an id (CE-1); no at-rest uniqueness lint. |
| G-D3 | §8.3 | EXISTING CE-14 | none | Links and `file::symbol` resolve. |
| G-D4 | §8.3 | EXISTING CE-14 | none | Liveness near the top. |
| G-D5 | §8.3 | EXISTING CE-14 | none | Typed counts. |
| G-D6 | §8.3 | EXISTING CE-5 | none | The decision index is CE-5's; its check is regeneration equality. |
| G-D7 | §8.3 | EXISTING CE-14 | none | Signal budgets. |
| G-D8 | §8.3 | EXISTING CE-14 | none | `banner set` stamps one key at write time; no at-rest check. |
| G-D9 | §8.3 | EXISTING CE-14 | none | Provenance on tuned config. |
| G-D10 | §8.3 | EXISTING CE-1 (built) | `store.py::Store.body_problem`; `tests/test_store.py::test_editing_an_append_only_body_fails_lint_and_amend_passes` | Built in `682b0fc`. |
| G-D11 | §8.3 | EXISTING CE-1 (built) | `store.py::Store.lint_bundles`; `tests/test_store.py::test_an_md_without_type_in_a_bundle_directory_fails_lint` | Built in `682b0fc`; the index list shape is not checked. |
| schema | §8.3 | EXISTING CE-1 (built) | `store.py::Store.lint`; `tests/test_store.py::test_a_new_record_that_breaks_its_schema_is_refused_and_nothing_is_written` | Built in `682b0fc`. |
| G-R1 | §8.3 | EXISTING CE-8 (built) | `working.py::Engine.lint_routes`; `tests/test_working.py::test_routes_print_and_a_missing_routed_path_fails_lint` | Built in `d5c36be`. |
| G-W1 | §8.4 | EXISTING CE-2 (built) | `working.py::Engine.lint_working`; `tests/test_working.py::test_a_banner_older_than_the_newest_close_fails_lint` | Built in `eef8fdc`. |
| G-W2 | §8.4 | EXISTING CE-2 (built) | `Engine.lint_working`; `test_working.py::test_more_than_two_pauses_in_a_row_fail_lint` | Built in `eef8fdc`. |
| G-W3 | §8.4 | EXISTING CE-2 (built) | `Engine.lint_working`, `Engine.expire_batons`; `test_working.py::test_a_baton_older_than_two_sessions_fails_lint_and_housekeeping_files_a_task` | Built in `eef8fdc`. |
| G-W4 | §8.4 | EXISTING CE-2 (built) | `Engine.lint_working`; `test_working.py::test_state_and_status_disagreeing_fails_lint` | Built in `eef8fdc`. |
| G-W5 | §8.4 | EXISTING CE-2 (built) | `Engine.lint_working`; `test_working.py::test_tier_caps_fail_lint` | Built in `eef8fdc`. |
| G-W6 | §8.4 | EXISTING CE-2 (built) | `Engine.session_close`, `Engine.lint_working`; `test_working.py::test_the_newest_close_needs_its_receipts_at_rest` | Built in `eef8fdc`. |
| G-W7 | §8.4 | EXISTING CE-14 | partial: `working.py::BOARD_OWNED` refused by `task set` | Write-time refusal is built; the at-rest check against the op log is not. |
| G-W8 | §8.4 | EXISTING CE-2 (built) | `Engine.session_close`; `test_working.py::test_close_refuses_while_an_overdue_question_is_unraised` | Built in `eef8fdc` (write-time refusal). |
| G-W9 | §8.4 | EXISTING CE-6 | none | Comes with `hk.close`. |
| G-W10 | §8.4 | DEFERRED | none | Counts housekeeping writes; only one `hk_` operation exists. Un-defer: CE-6 or CE-12 runs real housekeeping. |
| G-W11 | §8.4 | DEFERRED | none | Its window is to be measured in the §8.0.3 trial (CE-7). Un-defer: the trial reports; stub repair itself is CE-6. |
| G-V1 | §8.5 | EXISTING CE-17 | none | Run ledger and tiles. |
| G-V2 | §8.5 | DEFERRED | none | §11.2 trigger "the suite is large" not hit. Un-defer: a suite whose drops go unnoticed. |
| G-V3 | §8.5 | EXISTING CE-17 | none | The gate-run lock belongs with the run ledger. |
| G-V4 | §8.5 | PROSE-ONLY | global `CLAUDE.md` § Assurance traps; `CLAUDE.md` § Gate | Exit-code hygiene is how a command is typed; a rule, not a tool. |
| G-M1 | §8.5 | EXISTING CE-8 (built) | `tests/test_repo_records.py::test_this_repos_records_pass_lint` | Built in `c96ec5b`: lint runs inside the gate on this repo's records. |

## Other sections (context, not counted)

| § | Home |
|---|---|
| §5.5 several writers | built: `lock.py`, session keys under the lock (CE-1, CE-2) |
| §8.0 to §8.0.2 engine, kinds, entry points | built: CE-1, CE-2, CE-3, CE-8 |
| §8.0.3 trial before adoption | CE-4 (baseline, closed), CE-7 (trial) |
| §9.1 to §9.3 storage and OKF | built: `okf.py` (CE-1) |
| §9.4 later | DEFERRED by the section itself: vector search, source graph, memory architecture |
| §10, §11 layout and adoption | CE-15, then CE-7 and CE-11; §11.4 decision import is CE-5 |

## Totals (2026-10-12, not regenerable: counted from the tables above at `40eada6`)

| Class | Components | Rituals | Guards | All |
|---|---|---|---|---|
| EXISTING (built) | 7 | 3 | 12 | 22 |
| EXISTING (open item) | 5 | 6 | 15 | 26 |
| NEW | 7 | 4 | 5 | 16 |
| PROSE-ONLY | 2 | 1 | 1 | 4 |
| DEFERRED | 2 | 0 | 6 | 8 |
| **Rows** | **23** | **14** | **39** (38 G-ids plus schema) | **76** |

## Filed

- CE-25: intent chain tooling (charter goals, criteria, intake; G-I1, G-I2, G-T1, G-T2, G-T6), deps CE-14
- CE-26: method runbooks (§7.5, §6.6)
- CE-27: archive, freeze and promotion operations (§6.7, §7.3)
- CE-28: cross-repo owner-question index (§5.6), SOMEDAY, deps CE-15
- CE-29: unverified hazards and memory, SOMEDAY
- CE-30: coverage guard over this map and the board, deps CE-14
