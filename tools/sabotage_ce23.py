"""CE-23 sabotage table (DEC-11): break what each AC-26 to AC-29 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce23.py`. Unlike sabotage_ce2.py it never
edits the working tree: it copies the tree to a temp directory, sabotages the copy, and runs the
tests there with PYTHONPATH pointing at the copy's src/ (checked: the import must resolve inside
the copy). Several sessions share this checkout, and a sabotage written into it would be read,
or committed, by another session while it runs (global CLAUDE.md § Concurrent sessions).

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), for the reason in sabotage_ce2.py.
The patterns are exact source lines from 2026-10-12b; when the code moves, a pattern stops
matching and the script stops with an AssertionError naming it, rather than passing quietly.
"""
import os, pathlib, shutil, subprocess, sys, tempfile

PY_EXE = sys.executable
W = "src/context_engine/working.py"
R = "src/context_engine/review.py"
T = "tests/test_review.py"
S = [
 ("AC-26", W, '            if pri == "NOW" and rec.doc.get("review"):', "            if False:", T + " -k promote_to_now"),
 ("AC-26", W, '        if changes.get("review") is not None:', "        if False:", T + " -k outside_the_configured"),
 ("AC-26", R, "    if section is not None and any(ln.strip() in template", "    if False and any(ln.strip() in template", T + " -k placeholder"),
 ("AC-26", R, '            for k in ("why", "control"):', '            for k in ("why",):', T + " -k residual-without-control"),
 ("AC-27", R, "        if key(source, r.text) in have:\n            continue", "        if False:\n            continue", T + " -k reclose"),
 ("AC-27", W, "                filed.extend(self._file_residuals(rec, session, actor))", "                pass", T + " -k reclose"),
 ("AC-27", W, "        if not self.w.register:\n            raise Refusal(f\"{rec.id} has", "        if False:\n            raise Refusal(f\"{rec.id} has", T + " -k no_register_and"),
 ("AC-28", W, '                if probs:\n                    out.append(Failure("G-W12"', '                if False:\n                    out.append(Failure("G-W12"', T + " -k g_w12"),
 ("AC-28", W, "                if missing:", "                if False:", T + " -k g_w13"),
 ("AC-28", W, "        for p in R.entry_problems(es):", "        for p in []:", T + " -k g_w13"),
 ("AC-29", R, 'PACKAGED = "REGISTER.md"', 'PACKAGED = "REGISTR.md"', T + " -k packaged_register"),
 ("AC-29", R, 'PACKAGED = "REGISTER.md"', 'PACKAGED = "REGISTR.md"', T + " -k foreign_repo"),
 ("AC-29", W, "        if pointer:", "        if False:", T + " -k foreign_repo"),
]
IGNORE = shutil.ignore_patterns(".git", ".scratch", ".context", "__pycache__", "*.egg-info", ".pytest_cache")
ok = True
with tempfile.TemporaryDirectory() as tmp:
    copy = pathlib.Path(tmp) / "tree"
    shutil.copytree(".", copy, ignore=IGNORE)
    env = {**os.environ, "PYTHONPATH": str(copy / "src")}
    where = subprocess.run([PY_EXE, "-c", "import context_engine; print(context_engine.__file__)"], capture_output=True, text=True, cwd=copy, env=env).stdout.strip()
    assert pathlib.Path(where).resolve().is_relative_to(copy.resolve()), f"the copy imports {where}, not its own src/"
    for ac, f, old, new, sel in S:
        p = copy / f
        orig = p.read_text(encoding="utf-8")
        assert orig.count(old) == 1, (ac, old[:60])
        try:
            p.write_text(orig.replace(old, new), encoding="utf-8")
            path, *k = sel.split(" -k ")
            args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
            with tempfile.TemporaryDirectory() as cache:
                r = subprocess.run(args, capture_output=True, text=True, timeout=300, cwd=copy, env={**env, "PYTHONPYCACHEPREFIX": cache})
            last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
            red = r.returncode != 0 and "failed" in "".join(last)
            ok &= red
            print(f"{ac:5} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last}")
        finally:
            p.write_text(orig, encoding="utf-8")
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
sys.exit(0 if ok else 1)
