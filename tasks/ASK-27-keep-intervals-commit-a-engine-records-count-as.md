---
type: Question
id: ASK-27
title: 'Keep intervals commit A: engine records count as prose to gate.py and fuzz CI?'
brief: 'Recommend keep: fuzz on a ledger line tests unchanged code'
pri: LATER
state: open
deps: []
source: session 2026-11-02a
created: 2026-11-02
moved: 2026-11-02a
updated: 2026-11-02a
last_asked: 2026-11-02a
blocks: [CE-11]
---

## Context

The intervals cutover's commit A (3906abd) changes intervals' CI and gate: `tools/gate.py` and
`.github/workflows/fuzz.yml` treat `context.toml`, `docs/ledger/**` and `docs/archive/**` as prose.
Without it, every engine write (op log lines, ledger entries) makes the 14-minute gate stale and a
push starts a 30-60 minute fuzz run. The verifier read the diff: only those paths are exempted,
`multiinterval/` is unchanged, and the change's sabotage script went red 5/5 then green after restore.

## Options

- Keep commit A as it is.
- Drop commit A and accept full gate and fuzz runs after engine writes.
- Keep the gate change but leave fuzz.yml alone.

## Recommendation

Keep commit A: engine records are prose, and running fuzz on a ledger line spends CI time to test
code that did not change.
