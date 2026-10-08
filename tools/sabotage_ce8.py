"""CE-8 sabotage: each row breaks one thing, runs its test with a fresh bytecode cache, restores."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

ROWS = [
    ("stamp checks every id before writing any",
     "src/context_engine/working.py",
     "            if rec.kind.mode != \"append-only\":\n                raise Refusal(f\"{rid} is a {rec.kind.mode} record\", \"only append-only records carry body_sha\")\n",
     "",
     "tests/test_working.py::test_record_stamp_is_all_or_nothing_and_amend_appends"),
    ("an owner's words edited after the stamp",
     "docs/stories/US-11-rituals-without-python.md",
     "## Owner's words (verbatim)",
     "## Owner's words (verbatim, edited)",
     "tests/test_repo_records.py::test_this_repos_records_pass_lint"),
    ("a record left unstamped",
     "docs/decisions/DEC-1-own-repo-own-env.md",
     None, None,  # drop the body_sha line
     "tests/test_repo_records.py::test_this_repos_records_pass_lint"),
]

failed = 0
for name, rel, old, new, test in ROWS:
    path = ROOT / rel
    orig = path.read_bytes()
    text = orig.decode("utf-8")
    if old is None:
        lines = text.splitlines(keepends=True)
        broken = "".join(ln for ln in lines if not ln.startswith("body_sha:"))
    else:
        assert old in text, (name, "pattern not found")
        broken = text.replace(old, new, 1)
    assert broken != text, name
    try:
        path.write_bytes(broken.encode("utf-8"))
        env = {**os.environ, "PYTHONPYCACHEPREFIX": tempfile.mkdtemp(prefix="ce8sab-")}
        r = subprocess.run([PY, "-m", "pytest", "-q", "-x", test], cwd=ROOT, env=env, capture_output=True, text=True)
        red = r.returncode != 0
        first = next((ln for ln in r.stdout.splitlines() if ln.startswith("E ")), "")
        print(f"{'RED ' if red else 'GREEN (BAD)'} {name} -> {test}\n    {first[:200]}")
        failed += not red
    finally:
        path.write_bytes(orig)
sys.exit(failed)
