"""CE-185 sabotage table (DEC-11), and CE-186's three rows (2026-11-07e): break what each AC-41, AC-181, AC-182 and AC-183 test guards;
every run must go red, and the line it prints says why.

Run from the repo root: `<interpreter> tools/sabotage_ce185.py`. It restores every file it
touches. The patterns are exact source lines from 2026-11-06a; when the code moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing
quietly. Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), as in sabotage_ce2.py.
"""
import os, pathlib, re, subprocess, sys, tempfile

PY_EXE = sys.executable
SITE = "src/context_engine/site.py"
ST = "src/context_engine/store.py"
W = "src/context_engine/working.py"
CFG = "src/context_engine/config.py"
PAGES = ".github/workflows/pages.yml"
TS = "tests/test_site.py"
TD = "tests/test_decisions.py"
TC = "tests/test_ci.py"
S = [
    # AC-181: every record has a page and a listing link, and every link resolves
    ("AC-181", SITE, "        if closed:\n", "        if False:\n", TS + " -k holds_every_record"),
    ("AC-181", SITE, '            out |= {self.links[r.id]: self.record_page(r) for r in rs}', '            out |= {self.links[r.id]: self.record_page(r) for r in rs[1:]}', TS + " -k holds_every_record"),
    ("AC-181", SITE, '            rows.append(f"<tr><th>{esc(key)}</th><td>{self.link(text, 1)}</td></tr>")', '            rows.append(f"<tr><th>{esc(key)}</th><td>{self.link(text, 0)}</td></tr>")', TS + " -k holds_every_record"),
    # AC-181: it never writes into the tracked tree, nor over files
    ("AC-181", SITE, "        if out == root or not _ignored(root, rel):", "        if out == root:", TS + " -k refuses_a_tracked"),
    ("AC-181", SITE, "    if out.exists() and (not out.is_dir() or any(out.iterdir())):", "    if out.exists() and not out.is_dir():", TS + " -k refuses_a_tracked"),
    # AC-41, AC-183: no decision write stores an index
    ("AC-41", ST, '            self._log("new", rid, path, session, actor, list(doc.data.keys()), mechanical)\n', '            self._log("new", rid, path, session, actor, list(doc.data.keys()), mechanical)\n            if kind.type == "Decision":\n                (self.root / kind.dir / "index.md").write_text("- a stored index\\n", encoding="utf-8")\n', TD + " -k grouped_by_status"),
    ("AC-183", ST, '            self._log("new", rid, path, session, actor, list(doc.data.keys()), mechanical)\n', '            self._log("new", rid, path, session, actor, list(doc.data.keys()), mechanical)\n            if kind.type == "Decision":\n                (self.root / kind.dir / "index.md").write_text("- a stored index\\n", encoding="utf-8")\n', TS + " -k deprecated"),
    # AC-183: the deprecated key still loads, and orient names it
    ("AC-183", CFG, "    decision_index: str = \"\"  #", "    _gone: str = \"\"  #", TS + " -k deprecated"),
    ("AC-183", W, "        if self.w.decision_index:\n            stored =", "        if False:\n            stored =", TS + " -k deprecated"),
    # AC-182: the pages workflow is pinned to the floor, the op and the deploy
    ("AC-182", PAGES, '          python-version: "3.12"', '          python-version: "3.13"', TC + " -k pages_workflow"),
    ("AC-182", PAGES, '        run: python -m context_engine site build "$RUNNER_TEMP/site"', '        run: python -m context_engine site build _site', TC + " -k pages_workflow"),
    ("AC-182", PAGES, "  id-token: write\n", "", TC + " -k pages_workflow"),
    # CE-186 (2026-11-07e): the decisions' enum order, and record text escaped before and after each link
    ("AC-181", SITE, "        for status, tagged in D.groups(rows, statuses):", "        for status, tagged in D.groups(rows, ()):", TS + " -k holds_every_record"),
    ("AC-181", SITE, "            out.append(esc(text[at : m.start()]))", "            out.append(text[at : m.start()])", TS + " -k escaped_not_markup"),
    ("AC-181", SITE, "        out.append(esc(text[at:]))", "        out.append(text[at:])", TS + " -k escaped_not_markup"),
]
REASON = re.compile(r"^E\s+(.*)$", re.MULTILINE)
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    raw = p.read_bytes()  # restored byte for byte, whatever its line endings
    orig = raw.decode("utf-8").replace("\r\n", "\n")
    assert orig.count(old) == 1, (ac, f, old[:60])
    try:
        p.write_bytes(orig.replace(old, new).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        why = (REASON.findall(r.stdout) or ["(no E line)"])[0][:150]
        red = r.returncode != 0
        ok &= red
        print(f"{ac:6} {'RED ' if red else 'GREEN!'} {f.split('/')[-1]}: {old.strip().splitlines()[0][:50]!r} -> {last}\n         because: {why}")
    finally:
        p.write_bytes(raw)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
