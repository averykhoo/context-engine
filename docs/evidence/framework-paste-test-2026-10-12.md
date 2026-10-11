# Paste test: FRAMEWORK.md and manual-mode.md alone, 2026-10-12 (US-15, CE-24, CE-15)

FROZEN 2026-10-12a. Fixes made in the same session are listed at the end; everything else is
open on CE-24 (rituals runbook) or CE-15 (adoption kit).

**Question (owner, US-15):** if FRAMEWORK.md and the fallback runbook are pasted into a repo, is
that everything an agent needs to start using the framework, including with no Python?

**Method.** One read-only agent (2026-10-11, session before 2026-10-12a) read only
`docs/framework/FRAMEWORK.md` (1675 lines, at `950e615`) and `docs/runbooks/manual-mode.md`
(558 lines) in full, nothing else, and walked every ritual in two scenarios: **A**, the engine
is installable; **B**, no Python, everything by hand. Each step was classed OK, GAP, CONFLICT or
LEAK (text that only makes sense inside this repo). The session re-checked the key-format,
pause-trailer, close-order and ritual-section findings against both files first-hand.

**Verdict.** Day-to-day record operations work from the two files in both scenarios. Setting up
a new repo does not; the rituals as wholes have no by-hand section; housekeeping has almost no
fallback; and the ritual order is stated in three places that have drifted.

## Findings

### Bootstrap
- GAP (A, B) **`context.toml` schema**: §8.0 lists what the config holds but gives no key names
  or syntax. manual-mode § routes names the route fields; § "Record kinds here" is this repo's
  values, not a schema. `orient_max_bytes`, `read_max_bytes`, caps, cutoffs, models and the
  stale-stub window appear as names only.
- GAP (A) **install**: §6.9 "points the record engine at the repo, pinned to a version"; where
  from, the pin's syntax, and whether a scaffold command exists are not said.
- GAP (A, B) **first ledger and banner**: manual § session start needs a ledger preamble ending
  in `---` (content not given) and a `## Banner (<key>)` heading if `HANDOFF.md` exists; `banner
  set` only replaces an existing heading. Minting a key from an empty ledger is not described.
- GAP **charter and criteria**: §3.1 gives the charter's contents, not its format or goal-id
  scheme, yet a story's `goals` is required. The criteria format is open (`@pytest.mark.criterion`
  "such as"), so G-T2 cannot be checked by hand.
- CONFLICT §11.1 minimum set "orientation note with an inline board" vs manual-mode's board
  operations, which all write `tasks/<id>-<slug>.md`; the inline board has no hand procedure.
- CONFLICT §11.1 tooling lists "the tier-0 housekeeping script"; §8.0.2 says it is not built.
- GAP **the gate**: §11.1's minimum guards include G-D0, D1, D2, D3, D8, I2, T1, T2; manual §
  lint covers only the schema, G-D10, G-D11, G-W1 to G-W6 and G-R1. Neither file defines "the
  gate" for an adopting repo.

### Session start
- OK key minting, stub, `orient` by hand (manual § session start, § orient).
- CONFLICT **key format**: FRAMEWORK §5.5 "max(newest ledger key, banner key) + 1 letter" vs
  manual "earlier day than today → today's date + a"; FRAMEWORK's formula alone mints a key with
  a stale date. *Fixed 2026-10-12a.*
- GAP tier-1 checks (trace-, inbox-, question-check, §6.1): no prompts, no config keys; the
  SessionStart hook has no config. `kind: foreign` and `kind: abandoned` ledger entries (§6.10,
  §7.1) have no format and no hand section.

### Intake
- OK manual § record new, amend, stamp; § ask answer.
- CONFLICT §3.2 every story carries `via:`; manual-mode's story keys do not require it.
- Minor: two actor vocabularies (a decision's `actor:` §6.5 vs the writer actor in the op log)
  are easy to confuse. §3.1 "agents change the charter only through an owner question, then a
  decision" vs §6.2 "a decision ... or a charter edit".

### Board, questions, batons, pauses
- OK manual § task new/promote/close/list/show/section/comment: id allocation, slug, frontmatter
  order and body template are exact. OK § ask new/raised/later/answer; overdue rule matches §5.3.
  OK § baton add/done/expire, pause open/resume, consistent with §5.4 and §6.4.
- GAP §5.2 `## Design review` before promotion to NOW above the threshold; manual § task promote
  does not mention it (CE-23).
- GAP §5.6 cross-repo `~/.claude/owner-questions.md` "generated" by nothing named (CE-19).
- CONFLICT §6.10 "Agent commits carry a trailer `Session: <key>`. Commits without one are
  foreign" vs manual § pause open's commit `-m "pause PAU-n (<key>): ..."` with no trailer. The
  engine does the same: CE-22.

### Clean close
- OK manual § session close (exact template), § banner show/set, digest §5.6.
- CONFLICT within FRAMEWORK §6.3: the numbered steps include 1 (doc guards first) and 6a
  (pre-close housekeeping); "The order in practice" drops both, and so does `CLAUDE.md` §
  Rituals. *Fixed 2026-10-12a.*
- GAP §6 intro and P16 promise a by-hand section per ritual; manual-mode has per-operation
  sections only (no Session start, Intake, Clean close, Pause, Housekeeping). The ritual order
  lives only in FRAMEWORK §6 and `CLAUDE.md`. → CE-24.
- GAP §5.1 HANDOFF's "generated pointer to open batons and pause records" and "next session":
  no generator, no hand step.

### Housekeeping (§6.11)

| Item | Engine | By hand (manual-mode) |
|---|---|---|
| Expire batons and pauses into LATER tasks | `baton expire` (`hk.expire_batons`), writes and logs, no commit | § baton expire |
| Mechanical touch | `task touch --mechanical` | § task touch |
| Stamps | `record stamp` (not an `hk` op) | § record stamp |
| Stale stub → abandoned + baton | none | none |
| `last_asked` from hand-written `asked:` | none | none |
| Floor ratchets, regenerated indexes | none (CE-6) | none |
| Close by `Closes:` trailer | none (CE-6) | none |
| Commits → task comments, clearing committed pauses, foreign reconcile | none (tier 1, CE-6, CE-12) | none |

In scenario B tier-1 agents cannot exist (their allowlist is the `hk_` MCP tools), so all of it
falls to the main session, and P16's "housekeeping run" section does not exist. → CE-24.

### Push, CI, delegation
- GAP §6.8 states the policy; no watcher procedure, and "gate" is undefined for an adopter.
- §6.6 works but assumes Claude Code tools (`Explore`, `Workflow`, `fable`).

### Hashes with no Python
The algorithm is fully specified and reproducible with Git Bash `sha256sum`, PowerShell
`Get-FileHash` or `certutil -hashfile`. Gaps: hex case unstated (`Get-FileHash` and `certutil`
print uppercase); the `printf '%s\n' "$text" | sha256sum` line assumes `$text` is already
canonical; PowerShell 5.1 `-Encoding utf8` writes a BOM; where the banner ends at end of file is
unstated. *All but the canonicalisation example fixed 2026-10-12a.*

### This repo leaking into the pasted files
- FRAMEWORK: "(`context-engine`, this repo)" (§8.0); task ids CE-5 to CE-23 as build status;
  `spike/FINDINGS.md` (§6.1, §8.0.2); `docs/evidence/adhoc-baseline-2026-10-11.md` (§8.0.3);
  "this repo uses US, DEC, AC ..." (§3.2) next to §10's `S-n`/`D-n`; §7.4 "this repo has no
  register file"; archived `FRAMEWORK-v*.md` cited but not shipped.
- manual-mode: `source: US-11`; `tests/test_runbook.py`; AC and DEC ids as reasons; "`CLAUDE.md`
  § Gate"; the kinds table hard-codes `CE-n`, `DEC-n`, `US-n`; `.claude/settings.local.json`.

## Where each ritual is written (before CE-24)

| Ritual | FRAMEWORK | manual-mode | `CLAUDE.md` § Rituals |
|---|---|---|---|
| Session start | §6.1 | § session start, § orient (operations) | yes |
| Intake | §6.2 | § record new/amend, § ask answer | yes |
| Clean close | §6.3 (two orders) | § session close, § banner set, task ops | yes (engine order) |
| Pause | §6.4 | § session pause, § pause open | yes |
| Housekeeping | §6.11 | § baton expire only | no |
| Bootstrap, push/CI, delegation, foreign reconcile, promotion, rollback | §6.6–6.10, §6.13 | none | push only |

## Fixed in session 2026-10-12a
- FRAMEWORK §5.5 key formula now resets to `a` on a new day, as manual-mode and the engine do.
- FRAMEWORK §6.3 "order in practice" and `CLAUDE.md` § Rituals now include step 1 (lint first)
  and step 6a (pre-close housekeeping: `baton expire`).
- manual-mode § The two hashes: lowercase hex, no BOM, and the banner runs to end of file when
  no `## ` heading follows (as `ledger::read_banner` does).

Everything else: CE-24 (rituals runbook, single source of ritual order) and CE-15 (adoption kit:
config schema, install, skeletons, leaks). The pause commit trailer is CE-22.
