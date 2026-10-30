"""CE-42 sabotage table (DEC-11): break what each AC-160 to AC-164 test guards; every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce42.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-10-31 (session 2026-10-30a); when the
code moves, a pattern stops matching and the script stops with an AssertionError naming it, rather
than passing quietly. A run that selects no test counts as green, so a renamed test is noticed.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a same-length sabotage written in the
same second as the previous restore would otherwise run the stale .pyc (seen 2026-10-08d).
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
CR = "src/context_engine/criteria.py"
WK = "src/context_engine/working.py"
GU = "src/context_engine/guards.py"
T = "tests/test_criteria_write.py"

CASES = [
    ("append writes the row in LF whatever the file's ending", CR,
     'ls.insert(i + 1, row + _eol(last, raw))', 'ls.insert(i + 1, row + "\\n")', "-k appends_one_row"),
    ("rewrite rebuilds the whole row from stripped cells", CR,
     '    ls[line - 1] = body + eol\n',
     '    cells = G.row_cells(body)\n    for col, v in changes.items():\n        cells[col] = v\n    body = "| " + " | ".join(cells) + " |"\n    ls[line - 1] = body + eol\n', "-k rewrites_only_the_cells"),
    ("the G-T2 claim twin dropped", WK,
     '                    if cid not in found:\n', '                    if False:\n', "-k unless_g_t2_finds"),
    ("the G-T6 source twin dropped", WK,
     '                if problems:\n                    raise Refusal(problems[0][0] + " (G-T6)", problems[0][1])\n', '', "-k source_that_is_not"),
    ("the cell check lets a pipe through", CR,
     '    if len(G.PIPE_RE.split(value)) > 1:\n', '    if False:\n', "-k source_that_is_not"),
    ("no refusal for several tables without --under", CR,
     '        if len(found) > 1:\n            titles', '        if False:\n            titles', "-k never_guessed"),
    ("the read-back check dropped", WK,
     '        if len(mine) != 1 or shift(others)', '        if False and shift(others)', "-k read_back"),
    ("the next id ignores logged criterion.new lines", WK,
     'for i in rows_all | logged if', 'for i in rows_all if', "-k next_id_is_above"),
    ("a given id the op log created is accepted", WK,
     '        if cid in logged:\n', '        if False:\n', "-k next_id_is_above"),
    ("set no longer refuses an id leading two rows", WK,
     '            if len(found) > 1:\n                raise Refusal(f"{cid} leads', '            if False:\n                raise Refusal(f"{cid} leads', "-k no_row_two_rows"),
    ("criteria_rows no longer reports a duplicate id", GU,
     '        if r.id in seen:\n', '        if False:\n', "-k two_criterion_new"),
    ("G-D2 no longer scans criterion.new lines", GU,
     '("new", "import", "criterion.new")', '("new", "import")', "-k two_criterion_new"),
    ("the claimed-by column is not filled", WK,
     '            if claim and CR.CLAIMED_BY in place.table.header:\n                changes[', '            if False:\n                changes[', "-k claimed_by_cell"),
]

results = []
for what, rel, old, new, sel in CASES:
    path = os.path.join(ROOT, rel)
    orig = open(path, encoding="utf-8", newline="").read()
    assert orig.count(old) == 1, (what, old)
    open(path, "w", encoding="utf-8", newline="").write(orig.replace(old, new))
    try:
        env = {**os.environ, "PYTHONPATH": os.path.join(ROOT, "src"), "PYTHONPYCACHEPREFIX": tempfile.mkdtemp()}
        p = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", T, *sel.split()], cwd=ROOT, env=env, capture_output=True, text=True)
        last = (p.stdout.strip().splitlines() or ["?"])[-1]
        failed = [ln.split("::")[-1].split(" ")[0] for ln in p.stdout.splitlines() if ln.startswith("FAILED")]
        results.append((what, p.returncode if "failed" in last else 0, last, failed))
    finally:
        open(path, "w", encoding="utf-8", newline="").write(orig)
for what, rc, last, failed in results:
    print(f"{'RED' if rc else 'GREEN!'} | {what} | {last} | {', '.join(sorted(set(failed)))}")
sys.exit(0 if all(rc for _, rc, _, _ in results) else 1)
