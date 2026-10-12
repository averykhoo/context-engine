"""CE-21 sabotage table (sabotage rule, CLAUDE.md): break what each G-D0 test guards; every run
must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce21.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-10-12c; when the text moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing quietly.
Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), so a same-length sabotage never runs a
stale .pyc. G-T5 (mutation per criterion, CE-14) replaces this hand table.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
WK = "src/context_engine/working.py"
CF = "src/context_engine/config.py"
T = "tests/test_working.py"
ALL = " -k framework_pin or kit_block or missing_contract"
S = [
    ("always-pass", WK, "        rel = self.store.config.contract\n", "        return []\n        rel = self.store.config.contract\n", T + ALL),
    ("not-in-lint", WK, " + self.lint_contract()\n", "\n", T + " -k missing_contract"),
    ("major-only", WK, "!= want:\n                out.append(Failure(\"G-D0\", rel, f\"`framework: {value}` does not match", "!= want and v['major'] != want.split('.')[0]:\n                out.append(Failure(\"G-D0\", rel, f\"`framework: {value}` does not match", T + " -k another_major_minor"),
    ("no-synonym", WK, r'PIN_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.\*)?")', r'PIN_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)")', T + " -k equal_to_the_engines"),
    ("patch-accepted", WK, r'PIN_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.\*)?")', r'PIN_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?:\*|\d+))?")', T + " -k garbled"),
    ("draft-accepted", WK, r'PIN_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.\*)?")', r'PIN_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.\*|-draft)?")', T + " -k garbled"),
    ("no-line-ok", WK, "        if not pins:\n", "        if False:\n", T + " -k garbled"),
    ("indented-pin", WK, r'FRAMEWORK_LINE_RE = re.compile(r"^framework:', r'FRAMEWORK_LINE_RE = re.compile(r"^\s*framework:', T + " -k garbled"),
    ("marker-ignored", WK, "            if marker != want:\n", "            if False:\n", T + " -k kit_block"),
    ("missing-file", WK, "        if path is None or not path.is_file():\n", "        if path is None:\n", T + " -k missing_contract"),
    ("key-ignored", CF, '        contract=engine.get("contract", Config.contract),\n', "        contract=Config.contract,\n", T + " -k missing_contract"),
    ("key-unknown", CF, '"lock_timeout", "contract")', '"lock_timeout")', T + " -k missing_contract"),
    ("template", "src/context_engine/kit/context.toml.template", 'contract = "CLAUDE.md"', '# contract = "CLAUDE.md"', "tests/test_kit.py -k names_every_key"),
]
ok = True
for name, f, old, new, sel in S:
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8")
    crlf = "\r\n" in text
    norm = text.replace("\r\n", "\n")
    assert norm.count(old) == 1, (name, f, old[:60])
    try:
        bad = norm.replace(old, new)
        p.write_bytes((bad.replace("\n", "\r\n") if crlf else bad).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0
        ok &= red
        print(f"{name:16} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:50]!r:55} -> {last}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
sys.exit(0 if ok else 1)
