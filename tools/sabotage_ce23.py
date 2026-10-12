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
 ("AC-26", W, '\\"<text>\\"` from the template', '--file <f>` from the template', T + " -k no-section"),
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
 # review fixes, 2026-10-12b
 ("AC-26", R, '            for k in ("why", "control"):', '            for k in ("control",):', T + " -k residual-without-why"),
 ("AC-26", R, '        if r.cls in ("reduced", "residual"):', '        if r.cls in ("residual",):', T + " -k reduced-without-rung"),
 ("AC-26", R, '            elif r.cls == "residual" and rung == "eliminate":', "            elif False:", T + " -k residual-at-eliminate"),
 ("AC-26", R, '            elif r.cls == "reduced" and rung == "individual":', "            elif False:", T + " -k reduced-at-individual"),
 ("AC-26", R, "        if unknown:", "        if False:", T + " -k unknown-field"),
 ("AC-26", R, "        if not r.text:", "        if False:", T + " -k empty-risk"),
 ("AC-26", R, "    if not rv.risks:", "    if False:", T + " -k no-risk-line"),
 ("AC-26", W, "and its design review is not ready: {'; '.join(probs)}\",\n", "and its design review is not ready: {probs[0]}\",\n", T + " -k names_every_reason"),
 ("AC-26", W, "                    self._review_ready_at_now(rec, rec.doc.body, review)", "                    pass", T + " -k set_and_section"),
 ("AC-26", W, '            self._review_ready_at_now(rec, okf.set_section(rec.doc.body, name, text), rec.doc.get("review"))', "            pass", T + " -k set_and_section"),
 ("AC-26", R, "- eliminated: <a risk the design cannot produce>", "- eliminated: <a risk>", T + " -k runbook_carries"),
 ("AC-27", W, "                    self._review_kept(rec)", "                    pass", T + " -k unset_while"),
 ("AC-27", W, "        if probs:\n            raise Refusal(f\"{rec.id}'s design review", "        if False:\n            raise Refusal(f\"{rec.id}'s design review", T + " -k no_register_and"),
 ("AC-27", R, '    return (source, " ".join(risk.split()))', "    return (source, risk)", T + " -k reclose"),
 ("AC-27", W, "floor=self._inv_issued())", "floor=0)", T + " -k deleted_from_the_register"),
 ("AC-27", R, "    return max([floor, *(e.n for e in es)]) + 1", "    return max([0, *(e.n for e in es)]) + 1", T + " -k deleted_from_the_register"),
 ("AC-28", R, "        if not e.risk:", "        if False:", T + " -k g_w13"),
 ("AC-29", W, '            if not self.w.register:\n                raise Refusal("[working] has no', '            if False:\n                raise Refusal("[working] has no', T + " -k without_a_register"),
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
