"""CE-33 sabotage table (DEC-11): break what each G-D4 (liveness) and G-D5 (typed numbers) test
guards; every run must go red, by a failed assertion naming the expected reason.

Run from the repo root: `<interpreter> tools/sabotage_ce33.py [row-number ...]` (no numbers: every
row). It restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13c; when the code moves, a pattern stops matching and the script stops with an
AssertionError naming it, rather than passing quietly. G-T5 (mutation per criterion) replaces this
hand table.

A row is red only when pytest exits 1 with a failed test, no `E` line names an exception other
than an AssertionError (a NameError from a broken sabotage is not a red), and the `E` lines carry
the row's expected reason. Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a
same-length sabotage written in the same second as the previous restore would otherwise run the
stale .pyc (seen 2026-10-08d).
"""
import os, pathlib, re, subprocess, sys, tempfile

PY_EXE = sys.executable
G = "src/context_engine/guards.py"
C = "src/context_engine/config.py"
T = "tests/test_guards.py"
R = "tests/test_repo_records.py"
S = [
 # -- G-D4: the declaration forms and the window
 (G, 'DECLARED_RE = re.compile(rf"^\\s*(?:', 'DECLARED_RE = re.compile(rf"^.*?(?:', T + " -k each_declaration", "docs/f.md: declares no liveness"),
 (G, "    for i, line in enumerate(lines[:window]):", "    for i, line in enumerate(lines):", T + " -k each_declaration", "docs/g.md: declares no liveness"),
 (G, '                return Liveness(None, i + 1, f"line {i + 1}: ', '                return Liveness()  # f"line {i + 1}: ', T + " -k each_declaration", "LIVNG"),
 (G, "            m = FM_LIVENESS_RE.match(line)\n", "            m = None\n", T + " -k each_declaration", "docs/b.md"),
 (G, "        if ARCHIVED_RE.match(line):", "        if False:", T + " -k each_declaration", "docs/d.md"),
 (G, '    lines = text.lstrip("\\ufeff").split("\\n")\n    end = None', '    lines = text.split("\\n")\n    end = None', T + " -k each_declaration", "docs/j.md"),
 (G, "    for i, line in enumerate(lines[:window]):", "    for i, line in reversed(list(enumerate(lines[:window]))):", T + " -k history_doc", "plan-2026-10-13.md"),
 # -- G-D4: liveness_given
 (G, "            word = own.word or (give[0] if give else None)", "            word = own.word", T + " -k liveness_given", "FRAMEWORK-v0.1.md: declares no liveness"),
 (G, "        if not hits:\n", "        if False:\n", T + " -k liveness_given", "matches no file"),
 (G, "            if own.word and give and own.word != give[0]:", "            if False:", T + " -k liveness_given", "gives it FROZEN"),
 (C, "        if word not in LIVENESS:", "        if False:", T + " -k liveness_given", "DID NOT RAISE"),
 (C, '        if not glob or PureWindowsPath(glob).anchor or ".." in PureWindowsPath(glob).parts:', "        if not glob:", T + " -k liveness_given", "DID NOT RAISE"),
 (C, '    if "liveness_lines" in g and g["liveness_lines"] < 1:', "    if False:", T + " -k liveness_given", "DID NOT RAISE"),
 # -- G-D4: history and ACTIVE-PLAN
 (G, '            if word == "LIVING" and _under(rel, g.history):', "            if False:", T + " -k history_doc", "sits in a history directory"),
 (G, "                if not named:\n", "                if not named and False:\n", T + " -k history_doc", "names no board item"),
 (G, "                elif not any(board[i] for i in named):", "                elif False:", T + " -k history_doc", "is closed"),
 (G, '    return any(rel == d.rstrip("/") or rel.startswith(d.rstrip("/") + "/") for d in dirs)', "    return False", T + " -k history_doc", "sits in a history directory"),
 # -- G-D4: switches and empty extraction
 (G, "    if g.liveness and read == 0:", "    if False:", T + " -k is_off_while_both", "checks nothing there"),
 (G, '                out.append(Failure("G-D4", CONFIG_NAME, f"[guards] {name} names {rel}, which does not exist"', '                continue\n                out.append(Failure("G-D4", CONFIG_NAME, f"[guards] {name} names {rel}, which does not exist"', T + " -k is_off_while_both", "nowhere.md, which does not exist"),
 (G, "    return caps(e) + ids(e) + links(e) + liveness(e) + numbers(e)", "    return caps(e) + ids(e) + links(e) + numbers(e)", T + " -k is_off_while_both", "declares no liveness"),
 # -- G-D4 on this repo: the declarations are read, and the frozen provenance is given
 ("README.md", "\nLIVING. Status: pre-alpha.", "\nStatus: pre-alpha.", R, "G-D4 README.md: declares no liveness"),
 ("context.toml", '"docs/framework/FRAMEWORK-v0.*.md" = "FROZEN"', '"docs/framework/FRAMEWORK-v9.*.md" = "FROZEN"', R, "FRAMEWORK-v0.1.md: declares no liveness"),
 # -- G-D5: the count and P5's forms
 (G, "        if DATED_RE.search(line):\n            continue\n        bare = QUOTED_RE", "        if False:\n            continue\n        bare = QUOTED_RE", T + " -k count_of_the_tree", "1157 tests"),
 (G, "        bare = QUOTED_RE.sub(lambda m: \" \" * len(m.group(0)), line)\n        for m in rx", "        bare = line\n        for m in rx", T + " -k count_of_the_tree", "line 7"),
 (G, "            if not BOUND_RE.search(bare[: m.start()]):", "            if True:", T + " -k count_of_the_tree", "2 entries"),
 (G, 'COUNT_NUMBER = rf"(?<![\\w.,\\-§#/])(?:\\d+(?:,\\d{{3}})*|{SPELLED})"', 'COUNT_NUMBER = rf"(?<![\\w.,\\-§#/])(?:\\d+(?:,\\d{{3}})*)"', T + " -k count_of_the_tree", "seven steps"),
 (G, 'COUNT_NUMBER = rf"(?<![\\w.,\\-§#/])', 'COUNT_NUMBER = rf"(?<![\\w])', T + " -k count_of_the_tree", "6 rituals"),
 (G, 'COUNT_NUMBER = rf"(?<![\\w.,\\-§#/])(?:\\d+(?:,\\d{{3}})*|', 'COUNT_NUMBER = rf"(?<![\\w.,\\-§#/])(?:\\d+|', T + " -k count_of_the_tree", "1,157 tests"),
 (G, 'COUNT_ADJ = r"(?:(?:open|closed|new)\\s+)?"', 'COUNT_ADJ = r""', T + " -k count_of_the_tree", "12 open tasks"),
 (G, "    for n, line in prose(text):\n        if DATED_RE", "    for n, line in enumerate(text.split(\"\\n\"), 1):\n        if DATED_RE", T + " -k count_of_the_tree", "40 tests"),
 (G, "(?:{'|'.join(map(re.escape, nouns))})", "(?:tests|components|steps|tasks|rows)", T + " -k count_of_the_tree", "23 components"),
 (C, "    if not nouns or bad:", "    if False:", T + " -k count_of_the_tree", "DID NOT RAISE"),
 # -- G-D5: the banner escape, liveness_given, empty extraction
 (G, '        if liveness_of(e, rel, text, table) in ("FROZEN", "ACTIVE-PLAN"):', "        if False:", T + " -k frozen_or_active_plan", "frozen.md"),
 (G, "    hit = table.get(rel)\n", "    hit = None\n", T + " -k frozen_or_active_plan", "v0.1.md"),
 (G, "    if scanned == 0 and not out:", "    if False:", T + " -k frozen_or_active_plan", "checks nothing"),
 # -- G-D5 on this repo: a count typed into a LIVING doc
 ("README.md", "Nothing here is usable yet.", "Nothing here is usable yet; 552 tests pass.", R, "G-D5 README.md: line 9: `552 tests` is a count"),
]
only = {int(a) for a in sys.argv[1:]}
ok = True
reds = 0
for n, (f, old, new, sel, reason) in enumerate(S, 1):
    if only and n not in only:
        continue
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8").replace("\r\n", "\n")  # a CRLF checkout (autocrlf) matches too
    assert text.count(old) == 1, (n, f, old[:60], text.count(old))
    try:
        broken = text.replace(old, new, 1)
        p.write_bytes((broken.replace("\n", "\r\n") if b"\r\n" in orig else broken).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-vv", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        e_lines = [l for l in r.stdout.splitlines() if l.startswith("E ")]
        foreign = [l for l in e_lines if re.match(r"E\s+(\w+Error|\w+Exception)\b", l) and not re.match(r"E\s+(AssertionError|Failed)\b", l)]
        red = r.returncode == 1 and "failed" in "".join(last) and not foreign and any(reason in l for l in e_lines)
        ok &= red
        reds += red
        why = (foreign or [l for l in e_lines if reason in l] or e_lines or ["(no E line)"])[0].strip()[:110]
        print(f"{n:2} {'RED ' if red else 'GREEN!'} {f.rsplit('/', 1)[-1]:16} {old.strip().splitlines()[0][:44]!r:48} -> {last} {why}")
    finally:
        p.write_bytes(orig)
print(f"{reds} of {len(only) if only else len(S)} rows red")
sys.exit(0 if ok else 1)
