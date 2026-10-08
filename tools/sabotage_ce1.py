"""CE-1 sabotage table (DEC-11): break what each AC-1 to AC-9 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce1.py`. It restores every file it touches.
The patterns are exact source lines from 2026-10-08c; when the code moves, a pattern stops
matching and the script stops with an AssertionError naming it, rather than passing quietly.
G-T5 (mutation per criterion, CE-14) replaces this hand table.
"""
import pathlib, subprocess, sys

PY_EXE = sys.executable
S = [
 ("AC-1", "src/context_engine/okf.py", 'newline = "\\r\\n" if text.count("\\r\\n") * 2 > text.count("\\n") else "\\n"', 'newline = "\\n"', "tests/test_okf.py -k round_trips or one_key"),
 ("AC-1", "src/context_engine/okf.py", "self.fm_lines[start:end] = new", "self.fm_lines[start:end] = new; self.fm_lines[:] = _yaml_redump(self.fm_lines)", "tests/test_okf.py -k one_key"),
 ("AC-2", "src/context_engine/okf.py", "self.fm_lines[start:end] = new", "self.fm_lines[start:] = new", "tests/test_okf.py -k unknown_keys"),
 ("AC-3", "src/context_engine/store.py", 'if not okf.has_frontmatter(doc) or not doc.get("type"):', "if False:", "tests/test_store.py -k bundle_directory"),
 ("AC-4", "src/context_engine/store.py", "return [self.root / d for d in (kind.dir, *kind.extra_dirs)]", "return [self.root / kind.dir]", "tests/test_store.py -k closed_and_legacy"),
 ("AC-4", "src/context_engine/store.py", "        with self._lock():\n            used = self.ids_in_use(kind)", "        if True:\n            used = self.ids_in_use(kind)", "tests/test_store.py -k concurrent_allocations"),
 ("AC-5", "src/context_engine/store.py", "        probs = self.problems(kind, doc, path)\n        if probs:", "        probs = self.problems(kind, doc, path)\n        if False:", "tests/test_store.py -k schema"),
 ("AC-6", "src/context_engine/store.py", '"mechanical": mechanical,', '"mechanical": False,', "tests/test_store.py -k mechanical"),
 ("AC-6", "src/context_engine/store.py", "        if not session or not SESSION_RE.match(session):", "        if False:", "tests/test_store.py -k session_key"),
 ("AC-7", "src/context_engine/okf.py", 'canon = original_body(body).strip("\\n") + "\\n"', "canon = body", "tests/test_okf.py -k lf_and_crlf"),
 ("AC-8", "src/context_engine/store.py", "        if stamped != okf.body_sha(doc.body):", "        if False:", "tests/test_store.py -k append_only_body"),
 ("AC-9", "src/context_engine/store.py", "        with self._lock():\n            rec = self.get(record_id)\n            if rec.kind.mode != \"append-only\":\n                raise Refusal(f\"{record_id} is a {rec.kind.mode} record\", \"edit", "        if True:\n            rec = self.get(record_id)\n            if rec.kind.mode != \"append-only\":\n                raise Refusal(f\"{record_id} is a {rec.kind.mode} record\", \"edit", "tests/test_store.py -k same_record_lose_nothing"),
 ("AC-9", "src/context_engine/store.py", "        with self._lock():\n            rec = self.get(record_id)\n            for key, value in changes.items():", "        if True:\n            rec = self.get(record_id)\n            for key, value in changes.items():", "tests/test_store.py -k same_record_lose_nothing"),
]
HELPER = "\ndef _yaml_redump(lines):\n    out = io.StringIO(); _yaml().dump(_yaml().load(''.join(lines)), out); return out.getvalue().splitlines(keepends=True)\n"
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_text(encoding="utf-8")
    assert orig.count(old) == 1, (ac, old[:60])
    try:
        p.write_text(orig.replace(old, new) + (HELPER if "_yaml_redump" in new else ""), encoding="utf-8")
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        r = subprocess.run(args, capture_output=True, text=True, timeout=300)
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0
        ok &= red
        print(f"{ac:5} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last}")
    finally:
        p.write_text(orig, encoding="utf-8")
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
