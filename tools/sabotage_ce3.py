"""CE-3 sabotage table (DEC-11): break what each AC-18 and AC-19 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce3.py`. It restores every file it touches.
Same method as `tools/sabotage_ce2.py`: exact source patterns (a moved pattern stops the script
with an AssertionError), and a fresh bytecode cache per run (PYTHONPYCACHEPREFIX).
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
M = "src/context_engine/mcp.py"
O = "src/context_engine/ops.py"
C = "src/context_engine/cli.py"
T = "tests/test_mcp.py"
S = [
 ("AC-18", C, '    groups.add_parser("orient")\n', '    groups.add_parser("orient")\n    groups.add_parser("whoami")\n', T + " -k every_cli_subcommand"),
 ("AC-18", M, "    for o in ops.OPS.values():", "    for o in list(ops.OPS.values())[:-1]:", T + " -k every_cli_subcommand"),
 ("AC-18", C, 'for name in ("deps", "add", "remove", "blocks"):', 'for name in ("add", "remove", "blocks"):', T + " -k same_function"),
 ("AC-18", M, "            _, text = o.fn(e, c, **kw)", '            _, text = o.fn(e, c, **{k: v for k, v in kw.items() if k != "mechanical"})', T + " -k same_function"),
 ("AC-18", M, "            _, text = o.fn(e, c, **kw)", '            _, text = (ops.task_list if o.name == "task_list" else o.fn)(e, c, **kw)', T + " -k same_function"),
 ("AC-19", O, "    return 0, e.comment(id, text, mechanical=mechanical, **c.kw)", '    return 0, e.comment(id, text, mechanical=mechanical, **c.kw) + chr(10) + \"more\"', T + " -k one_line"),
 ("AC-19", M, '        return text if o.write or o.name == "orient" else cap(text, e.w.read_max_bytes, o.rest)', "        return text", T + " -k over_the_cap"),
 ("AC-19", M, "    budget = limit - len(note.encode()) - 8", "    budget = limit", T + " -k never_exceeds"),
 # the caller, refusals and the entry point
 ("caller", M, "            state.session, state.actor = c.session, c.actor", "            pass", T + " -k remembered"),
 ("refusal", M, "            raise ToolError(str(r)) from r", "            raise", T + " -k remembered"),
 ("stdio", M, '    server(ap.parse_args(argv).root).run("stdio")', '    server(".").run("stdio")', T + " -k stdio"),
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
        print(f"{ac:7} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:55]!r:60} -> {last}")
    finally:
        p.write_text(orig, encoding="utf-8")
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
