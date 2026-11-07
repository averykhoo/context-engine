"""CE-150 sabotage table (DEC-11): break what the AC-40 and AC-160 tests of CE-150 guard; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce150.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-11-08 (session 2026-11-07e); when the
code moves, a pattern stops matching and the script stops with an AssertionError naming it, rather
than passing quietly. A run that selects no test counts as green, so a renamed test is noticed.
Same harness as tools/sabotage_ce42.py: each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX).
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
WK = "src/context_engine/working.py"
TD = "tests/test_decisions.py"
TC = "tests/test_criteria_write.py"
RAW = r're.findall(r"^\|\s*([A-Z]+-\d+)\s*\|", {x}, re.MULTILINE)'  # the raw row regex CE-150 removed
ROWS = r'rows = {cells[0] for t in G.table_blocks(raw.replace("\r\n", "\n")) for _, cells in t.body if cells and G.ROW_ID_RE.fullmatch(cells[0])}'

CASES = [
    ("decision link reads the criteria file with the raw row regex, not criteria_rows", WK,
     '        rows, problems = G.criteria_rows(G._text(path))\n        return {r.id for r in rows}, problems',
     '        return set(' + RAW.format(x="G._text(path)") + '), []', TD, "-k lint_reads_its_row"),
    ("decision link counts every id in the criteria file, prose included", WK,
     '        return {r.id for r in rows}, problems', '        return set(G.ID_RE.findall(G._text(path))), problems', TD, "-k checks_the_target"),
    ("the refusal drops the unreadable-table hint", WK,
     '                hint = f"; lint cannot read part of {self.w.criteria} ({unread[0][0]})" if unread else ""', '                hint = ""', TD, "-k lint_reads_its_row"),
    ("id allocation reads the raw row regex, which misses an indented row and sees a fence", WK,
     ROWS, 'rows = set(' + RAW.format(x=r'raw.replace("\r\n", "\n")') + ')', TC, "-k counts_an_indented_row"),
    ("id allocation counts only the rows criteria_rows reads", WK,
     ROWS, r'rows = {r.id for r in G.criteria_rows(raw.replace("\r\n", "\n"))[0]}', TC, "-k counts_an_indented_row"),
    ("link checks a criteria file even where none is set", WK,
     '        path = self.root / self.w.criteria if self.w.criteria else None', '        path = self.root / (self.w.criteria or "criteria.md")', TD, "-k no_criteria_file"),
]

results = []
for what, rel, old, new, test, sel in CASES:
    path = os.path.join(ROOT, rel)
    orig = open(path, encoding="utf-8", newline="").read()
    assert orig.count(old) == 1, (what, old)
    open(path, "w", encoding="utf-8", newline="").write(orig.replace(old, new))
    try:
        env = {**os.environ, "PYTHONPATH": os.path.join(ROOT, "src"), "PYTHONPYCACHEPREFIX": tempfile.mkdtemp()}
        p = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", test, *sel.split()], cwd=ROOT, env=env, capture_output=True, text=True)
        last = (p.stdout.strip().splitlines() or ["?"])[-1]
        failed = [ln.split("::")[-1].split(" ")[0] for ln in p.stdout.splitlines() if ln.startswith("FAILED")]
        results.append((what, p.returncode if "failed" in last else 0, last, failed))
    finally:
        open(path, "w", encoding="utf-8", newline="").write(orig)
for what, rc, last, failed in results:
    print(f"{'RED' if rc else 'GREEN!'} | {what} | {last} | {', '.join(sorted(set(failed)))}")
sys.exit(0 if all(rc for _, rc, _, _ in results) else 1)
