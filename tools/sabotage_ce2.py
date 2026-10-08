"""CE-2 sabotage table (DEC-11): break what each AC-10 to AC-17 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce2.py`. It restores every file it touches.
The patterns are exact source lines from 2026-10-08d; when the code moves, a pattern stops
matching and the script stops with an AssertionError naming it, rather than passing quietly.
G-T5 (mutation per criterion, CE-14) replaces this hand table.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX). Without it a sabotage of the same
byte length written in the same second as the previous restore runs the stale .pyc, and the row
passes green on unsabotaged code: seen 2026-10-08d (`"branch": branch,` -> `"branch": "main",`).
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
W = "src/context_engine/working.py"
LG = "src/context_engine/ledger.py"
T = "tests/test_working.py"
S = [
 ("AC-10", W, "        with self.store.lock():\n            led = self.read_ledger()\n            b = self.banner()", "        if True:\n            led = self.read_ledger()\n            b = self.banner()", T + " -k concurrent_starts"),
 ("AC-10", W, "L.newest([*led.keys(), b.key if b else None])", "L.newest(led.keys())", T + " -k newer_of_ledger"),
 ("AC-10", W, "            led.entries.insert(0, L.Entry(key, \"open\", L.render_open(key, _now(), actor)))", "            pass", T + " -k newer_of_ledger"),
 ("AC-11", W, 'for name in ("guards", "read"):\n            if not (receipts', 'for name in ():\n            if not (receipts', T + " -k malformed"),
 ("AC-11", W, "if not 1 <= len(summary) <= 7:", "if False:", T + " -k malformed"),
 ("AC-11", W, "            if missing:", "            if False:", T + " -k next_tier"),
 ("AC-11", W, "            if unraised:", "            if False:", T + " -k overdue_question"),
 ("AC-11", LG, 'f"## {key} · kind: pause\\n\\n"', 'f"## {key} · kind: close\\n\\n"', T + " -k pause_writes"),
 ("AC-12", W, 'changes = {"state": "closed", "status": "deprecated", "closed": session, "moved": session}', 'changes = {"state": "closed", "closed": session, "moved": session}', T + " -k in_place"),
 ("AC-12", W, '        if not msg or not msg.strip():\n            raise Refusal(f"closing', '        if False:\n            raise Refusal(f"closing', T + " -k without_a_message"),
 ("AC-12", W, 'if (state == "closed") != (status == "deprecated"):', "if False:", T + " -k disagreeing"),
 ("AC-13", W, "        for r in self.board_heads(kinds):", "        for r in [r for k in (kinds or self._board()) for r in self.store.records(k)]:", T + " -k without_reading_bodies"),
 ("AC-13", W, "        rows.sort(", "        rows.reverse()\n        (lambda **k: None)(", T + " -k without_reading_bodies"),
 ("AC-13", W, "if label and label not in", "if False and label not in", T + " -k without_reading_bodies"),
 ("AC-14", W, '"branch": branch,', '"branch": "main",', T + " -k pause_open"),
 ("AC-14", W, "            dirty.append(path.split(\" -> \")[-1].strip('\"'))", "            pass", T + " -k pause_open"),
 ("AC-14", W, '        self._git("commit", "-q", "--only", "-m", f"pause {rec.id} ({session}): {fields[\'title\'][:60]}", "--", rel)', '        self._git("add", "-A"); self._git("commit", "-q", "-m", "pause")', T + " -k pause_open"),
 ("AC-15", W, '                if self._age(led, r.doc.get("session")) >= self.w.baton_max_age:\n                    out.append(Failure("G-W3"', '                if False:\n                    out.append(Failure("G-W3"', T + " -k older_than_two"),
 ("AC-15", W, '            if self._age(led, r.doc.get("session")) < self.w.baton_max_age:\n                continue', "            if True:\n                continue", T + " -k older_than_two"),
 ("AC-15", W, "return len(led.after(key)) if key else 10**6", "return len(led.after(key)) + 1 if key else 10**6", T + " -k older_than_two"),
 ("AC-16", W, "if now.sha != seen_hash:", "if False:", T + " -k stale_hash"),
 ("AC-16", LG, 'hashlib.sha256(section.strip("\\n").encode("utf-8"))', 'hashlib.sha256(m.group("key").encode("utf-8"))', T + " -k stale_hash"),
 ("AC-17", W, "return fit(head, sections, self.w.orient_max_bytes)", "return fit(head, sections, 10**9)", T + " -k never_exceeds"),
 ("AC-17", W, 'key=lambda r: (r.doc.get("session") != session,', 'key=lambda r: (r.doc.get("session") == session,', T + " -k every_part"),
 ("AC-17", W, "for i in dict.fromkeys(pending + overdue)", "for i in dict.fromkeys(pending)", T + " -k every_part"),
 ("AC-17", W, 'others = [e for e in led.entries if e.kind == "open" and e.key != session]', "others = []", T + " -k every_part"),
 ("AC-17", W, 'for name in ("Traps", "Read first"):', 'for name in ("Read first",):', T + " -k every_part"),
 # guards and checks CE-2 added beyond its criteria
 ("G-W1", W, "if key_order(b.key) < key_order(newest_close):", "if False:", T + " -k banner_older"),
 ("G-W2", W, "if run > self.w.max_pauses:", "if False:", T + " -k pauses_in_a_row"),
 ("G-W5", W, 'if len(holders) > cap or (pri == "NOW" and open_ and len(holders) != cap):', "if len(holders) > cap:", T + " -k tier_caps"),
 ("G-W6", W, "if not last.receipt(name):", "if False:", T + " -k receipts_at_rest"),
 ("types", "src/context_engine/store.py", "            if _wrong_type(want, doc.get(key)):", "            if False:", T + " -k wrong_declared_type"),
 ("types", "src/context_engine/store.py", "return dt.date.fromisoformat(text.strip())", "return text.strip()", T + " -k coerced"),
 ("caps", W, '            raise Refusal(f"{pri} already holds', '            return\n            raise Refusal(f"{pri} already holds', T + " -k promote_respects"),
]
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_text(encoding="utf-8")
    assert orig.count(old) == 1, (ac, old[:60])
    try:
        p.write_text(orig.replace(old, new), encoding="utf-8")
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0
        ok &= red
        print(f"{ac:5} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last}")
    finally:
        p.write_text(orig, encoding="utf-8")
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
