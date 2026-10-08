"""A separate OS process for the concurrency tests: waits at a start gate, then writes.

usage: _worker.py ROOT GATE OP N TAG [ID]
  new    N TAG      create N tasks titled "<TAG> <i>"
  amend  N TAG ID   amend record ID N times with "<TAG> <i>"
  set    N TAG ID   set field `note_<TAG>` on record ID N times
  start  N TAG      run `session.start` N times (the repo needs a [working] ledger)
"""

import sys
import time
from pathlib import Path

from context_engine.store import Store
from context_engine.working import Engine

root, gate, op, n, tag = sys.argv[1:6]
target = sys.argv[6] if len(sys.argv) > 6 else None
store = Store(root)
deadline = time.monotonic() + 30
while not Path(gate).exists():
    if time.monotonic() > deadline:
        sys.exit("start gate never opened")
    time.sleep(0.005)

kw = {"session": "2026-10-08c", "actor": f"process:worker-{tag}"}
for i in range(int(n)):
    if op == "new":
        store.new("task", {"title": f"{tag} {i}", "pri": "LATER", "state": "open"}, **kw)
    elif op == "amend":
        store.amend(target, f"{tag} {i}", **kw)
    elif op == "set":
        store.set(target, {f"note_{tag}": i}, **kw)
    elif op == "start":
        Engine(root).session_start(actor=kw["actor"])
    else:
        sys.exit(f"unknown op {op}")
