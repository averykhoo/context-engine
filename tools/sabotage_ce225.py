"""CE-225 sabotage table (DEC-11): break what each AC-210 test guards, and the G-D3 refactor;
every run must go red, and the line it prints says why.

Run from the repo root: `<interpreter> tools/sabotage_ce225.py`. It restores every file it
touches. The patterns are exact source lines from 2026-11-13a; when the code moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing
quietly. Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), as in sabotage_ce2.py.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
GD = "src/context_engine/guards.py"
TP = "tests/test_plan_check.py"
S = [
    ("AC-210", GD, 'NEW_MARK_RE = re.compile(r"[ \\t]?\\(new\\)")', 'NEW_MARK_RE = re.compile(r"[ \\t]*\\(new\\)")', TP + " -k at_most_one_space"),
    ("AC-210", GD, "            if NEW_MARK_RE.match(line, m.end()):", "            if NEW_MARK_RE.search(line, m.end()):", TP + " -k at_most_one_space"),
    ("AC-210", GD, '    return p == d or p.startswith(d + "/") or d.endswith("/" + p) or p.endswith("/" + d)', '    return p == d or p.startswith(d) or d.endswith("/" + p) or p.endswith("/" + d)', TP + " -k exempts_only_its_own_path"),
    ("AC-210", GD, '(r["symbol"] == s or r["symbol"].startswith(s + "."))', 'r["symbol"].startswith(s)', TP + " -k exempts_only_its_own_path"),
    ("AC-210", GD, "    if not cited and not new:", "    if False:", TP + " -k cites_nothing_fails"),
    ("AC-210", GD, '        return 1, "\\n".join([f"plan check: {rel}: {len(problems)} of {cited} cited fail"', '        return 0, "\\n".join([f"plan check: {rel}: {len(problems)} of {cited} cited fail"', TP + " -k dead_or_ambiguous"),
    ("AC-210", GD, "                v = path_verdict(files, span, here)", "                v = path_verdict(files, span, None)", TP + " -k what_g_d3_reports"),
    ("AC-210", GD, "        rel, here = p.as_posix(), None", "        rel, here = p.as_posix(), p.parent", TP + " -k own_directory"),
    ("AC-210", GD, "    if p := ambiguous_problem(files, file):\n        return p, False", "    if False:\n        return p, False", TP + " -k dead_or_ambiguous"),
    ("AC-210", GD, "    lines = list(prose(text))", '    lines = list(enumerate(text.split("\\n"), 1))', TP + " -k every_citation_resolves"),
    ("AC-210", GD, "    if not raw or not p.is_file():", "    if not raw:", TP + " -k names_no_file"),
    # verify-1 findings 1 and 2 (DEC-341 amended): a mark on a path that exists exempts nothing and fails
    ("AC-210", GD, "                elif is_pointer(span) and not path_exists(files, span, here):", "                elif is_pointer(span):", TP + " -k on_a_path_that_exists"),
    ("AC-210", GD, "                if not v and NEW_MARK_RE.match(line, m.end()):", "                if False:", TP + " -k on_a_path_that_exists"),
    ("AC-210", GD, "    return files.find(span) is not None or files.case_exact(span.rstrip(\"/\"), here) is not None", "    return files.case_exact(span.rstrip(\"/\")) is not None or files.case_exact(span.rstrip(\"/\"), here) is not None", TP + " -k on_a_bare_name"),
    ("AC-210", "src/context_engine/ops.py", "    return GD.plan_check(e.root, path)", "    return 0, GD.plan_check(e.root, path)[1]", TP + " -k exit_code_on_the_cli"),
    ("AC-210", "src/context_engine/cli.py", '    ("plan", "check"): "plan_check",', '    ("plan", "check"): "lint",', "tests/test_mcp.py -k plan_check"),
    ("AC-210", "docs/framework/FRAMEWORK.md", "   (P8); then `plan.check` (CLI", "   (P8); then `plan.chek` (CLI", TP + " -k build_ladder_runs_plan_check"),
    # the G-D3 refactor: the shared verdicts keep each failure's remedy (existing AC-107, AC-108 tests)
    ("AC-108", GD, "                    (bad if v[1] else unsure).append", "                    (unsure if v[1] else bad).append", "tests/test_guards.py -k ambiguous_bare_name_only_when"),
    ("AC-107", GD, "POINTER_REMEDY if v[1] else AMBIGUOUS_REMEDY", "AMBIGUOUS_REMEDY if v[1] else POINTER_REMEDY", "tests/test_guards.py -k backticked_paths_in_the_docs_paths"),
]
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8")
    assert text.count(old) == 1, (ac, old[:60])
    try:
        p.write_bytes(text.replace(old, new).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=600, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        why = [l for l in r.stdout.splitlines() if l.startswith("E ")][:1]
        red = r.returncode == 1 and bool(last) and "failed" in last[0]  # a test failed: not a collection error, nor none selected
        ok &= red
        print(f"{ac:6} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last} {why}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
