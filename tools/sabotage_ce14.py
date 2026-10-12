"""CE-14 sabotage table (DEC-11): break what each AC-43 to AC-51 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce14.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-10-12d; when the code moves, a
pattern stops matching and the script stops with an AssertionError naming it, rather than
passing quietly. G-T5 (mutation per criterion) replaces this hand table.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a same-length sabotage written in the
same second as the previous restore would otherwise run the stale .pyc (seen 2026-10-08d).
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
G = "src/context_engine/guards.py"
W = "src/context_engine/working.py"
C = "src/context_engine/config.py"
T = "tests/test_guards.py"
S = [
 ("AC-43", W, "return [f for f in found if f.guard not in off]", "return found", T + " -k guards_off"),
 ("AC-43", C, "    if unknown:\n        raise Refusal(f\"[guards] `off`", "    if False:\n        raise Refusal(f\"[guards] `off`", T + " -k guards_off"),
 ("AC-43", G, "        else:\n            yield rel, None", "        else:\n            pass", T + " -k guards_off"),
 ("AC-44", G, "if r.max_lines and len(lines) > r.max_lines:", "if False:", T + " -k g_d1"),
 ("AC-44", G, "and not ln.lstrip().startswith(\"|\")]", "]", T + " -k g_d1"),
 ("AC-44", G, "for f in sorted(p.rglob(\"*.md\")):", "for f in sorted(p.glob(\"*.md\")):", T + " -k g_d1"),
 ("AC-45", G, "            if len(paths) > 1:", "            if len(paths) > 2:", T + " -k g_d2"),
 ("AC-45", G, "            if rid in created:", "            if False:", T + " -k g_d2"),
 ("AC-46", G, "if not here.is_dir() or part not in os.listdir(here):", "if not (here / part).exists():", T + " -k g_d3"),
 ("AC-46", G, "frag not in anchors_of(hit)", "frag in ()", T + " -k g_d3"),
 ("AC-46", G, "missing = symbol_missing(hit, symbol)", "missing = None", T + " -k g_d3"),
 ("AC-46", G, "        if _deprecated(text):\n            continue", "        if False:\n            continue", T + " -k g_d3"),
 ("AC-46", G, "        if fence:\n            continue", "        if False:\n            continue", T + " -k g_d3"),
 ("AC-47", G, "for n, line in prose(_text(path), history=True):", "for n, line in prose(_text(path)):", T + " -k g_t3"),
 ("AC-47", G, "                    p = None if files.find(span) else", "                    p = None if True else", T + " -k g_t3"),
 ("AC-48", G, "        if warns > g.warn_max:", "        if warns > g.warn_max + 1:", T + " -k g_d7"),
 ("AC-48", G, "        if len(caps_) > g.bold_caps_max:", "        if False:", T + " -k g_d7"),
 ("AC-48", G, "            if glyph in body:", "            if False:", T + " -k g_d7"),
 ("AC-49", G, "    if len(banners) > 1:", "    if False:", T + " -k g_d8"),
 ("AC-49", G, "    if layered:", "    if False:", T + " -k g_d8"),
 ("AC-49", G, "        if layers:", "        if False:", T + " -k g_d8"),
 ("AC-49", G, r"(?:(?:[-*+]|\d+\.)\s+\**|\*\*)\s*", r"(?:[-*+]|\d+\.)?\s*\**\s*", T + " -k g_d8"),
 ("AC-50", G, "            if not PROVENANCE_RE.search(note):", "            if False:", T + " -k g_d9"),
 ("AC-50", G, "            elif not re.search(r\"wrong if|wrong as above\", note):", "            elif False:", T + " -k g_d9"),
 ("AC-50", G, "            elif re.search(r\"\\bexample\", note, re.IGNORECASE):", "            elif False:", T + " -k g_d9"),
 ("AC-50", G, "STRING_RE.sub('\"\"', line).partition(\"#\")", "line.partition(\"#\")", T + " -k g_d9"),
 ("AC-51", G, "                if v != str(op.get(\"session\")):", "                if False:", T + " -k g_w7"),
 ("AC-51", G, "            elif first is None or not re.fullmatch(KEY_RE, v) or key_order(v) >= key_order(first):", "            elif False:", T + " -k g_w7"),
 ("AC-51", G, "    if bad:\n        out.append(Failure(\"G-W7\"", "    if False:\n        out.append(Failure(\"G-W7\"", T + " -k g_w7"),
 ("AC-51", W, "found = self.lint_working() + G.tool_owned(self) if working", "found = self.lint_working() if working", T + " -k g_w7"),
 # data, not code: this repo's own docs under the new guards (AC-23 runs lint on them)
 ("AC-23", "docs/criteria.md", "# Criteria", "# Criteria `src/context_engine/nowhere.py`", "tests/test_repo_records.py"),
 ("AC-23", "HANDOFF.md", "## Banner (", "## 2026-10-01a notes\n\n## Banner (", "tests/test_repo_records.py"),
]
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8").replace("\r\n", "\n")  # a CRLF checkout (autocrlf) matches too
    assert text.count(old) == 1, (ac, old[:60], text.count(old))
    try:
        broken = text.replace(old, new)
        p.write_bytes((broken.replace("\n", "\r\n") if b"\r\n" in orig else broken).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0
        ok &= red
        print(f"{ac:5} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
