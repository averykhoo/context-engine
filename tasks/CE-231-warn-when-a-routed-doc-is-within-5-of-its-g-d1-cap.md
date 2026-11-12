---
type: Task
id: CE-231
title: Warn when a routed doc is within 5% of its G-D1 cap, before the next edit forces a cap raise
pri: NEXT
state: open
deps: []
goals: [G-7]
created: 2026-11-12
---

**Why:** `CLAUDE.md` is at 140/140 lines and 9,996/10,000 bytes, and `docs/runbooks/fan-out.md` is at 107/110 lines and 7,990/8,000 bytes (measured 2026-11-12 at HEAD `4797ac5`). G-D1 only fails when a cap is already crossed, so the next edit to either file forces a cap raise with no earlier warning.

**What:** a headroom warning at 95% of a route's `max_lines` or `max_bytes`, warning only, never a failure:
- `src/context_engine/guards.py`: add `cap_warnings(r, rel, text)` beside `cap_failures`, mirroring its line/byte counting; and `headroom(e)` over the routed components.
- `src/context_engine/cli.py` / `src/context_engine/ops.py`: add a `--headroom` flag to the `lint` subcommand; when set, print the warnings after the failure list, exit code unchanged (1 only if failures exist). Do not add warnings to `caps()` / `lint()` — lint must stay clean and a warning must not refuse a write.
- `docs/framework/FRAMEWORK.md` §8.3 G-D1: one sentence — the headroom warning, its 95% threshold, and that it never fails lint or refuses a write. Do not document it in `CLAUDE.md` (140/140 lines).
- `docs/criteria.md`: new row AC-208, modelled on AC-44.
- `tests/test_guards.py`: tests beside the existing G-D1 tests, marked `@pytest.mark.criterion("AC-208")`, including exact-boundary cases (19 of 20 lines warns, 18 does not; 380 of 400 bytes warns, 379 does not) and a file at 100% warning but not appearing in G-D1 failures.

**Acceptance:** `python -m context_engine lint` is clean; `python -m context_engine lint --headroom` warns for `CLAUDE.md` and `docs/runbooks/fan-out.md` only; `python -m pytest -q` is green; the new AC-208 tests go red when the warning is sabotaged, then pass again on restore.

**Open:** `max_width` is excluded from headroom (per-line, not a total). Do not raise any cap to silence the warning.

## Log

- 2026-11-12: closed: `cap_warnings` + `headroom` in guards.py, `--headroom` on `lint` (ops.py/cli.py), FRAMEWORK §8.3 sentence, AC-208 row, two AC-208 tests in tests/test_guards.py. Verification: `python -m pytest -q` 2107 passed, 1 failed (pre-existing: test_merge_settings_refuses_a_hard_linked_or_read_only_file, fails on clean HEAD as root); `lint` clean; `lint --headroom` warns for CLAUDE.md and docs/runbooks/fan-out.md only; sabotage (threshold to 100%) made the 95% boundary test go red, restored and green again.
