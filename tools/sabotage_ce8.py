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
    ("G-R1 never looks at the disk",
     "src/context_engine/working.py",
     "            if not r.optional and not (self.root / r.path).exists()\n",
     "            if False\n",
     "tests/test_working.py::test_routes_print_and_a_missing_routed_path_fails_lint"),
    ("G-R1 ignores `optional`",
     "src/context_engine/working.py",
     "            if not r.optional and not (self.root / r.path).exists()\n",
     "            if not (self.root / r.path).exists()\n",
     "tests/test_working.py::test_routes_print_and_a_missing_routed_path_fails_lint"),
    ("a route with no mode loads",
     "src/context_engine/config.py",
     '        for key in ("component", "path", "mode"):\n            if not r.get(key):',
     '        for key in ("component", "path"):\n            if not r.get(key):',
     "tests/test_working.py::test_a_malformed_route_is_refused_at_load"),
    ("a route with an unknown key loads",
     "src/context_engine/config.py",
     "        if extra:\n            raise Refusal(f\"route {n} has unknown key",
     "        if False:\n            raise Refusal(f\"route {n} has unknown key",
     "tests/test_working.py::test_a_malformed_route_is_refused_at_load"),
    ("record new fills no date",
     "src/context_engine/working.py",
     '            if key not in fields and k.types.get(key) == "date":',
     '            if False:',
     "tests/test_working.py::test_record_new_writes_a_stamped_decision_and_fills_only_now_keys"),
    ("record new guesses the actor",
     "src/context_engine/working.py",
     '        fields: dict[str, Any] = {"title": title}\n        fields.update({key: coerce(k, key, v)',
     '        fields: dict[str, Any] = {"title": title, "actor": "owner"}\n        fields.update({key: coerce(k, key, v)',
     "tests/test_working.py::test_record_new_writes_a_stamped_decision_and_fills_only_now_keys"),
    ("record new takes a board kind",
     "src/context_engine/working.py",
     '        if k.mode != "append-only":\n            raise Refusal(f"{kind!r} is a {k.mode} kind"',
     '        if False:\n            raise Refusal(f"{kind!r} is a {k.mode} kind"',
     "tests/test_working.py::test_record_new_writes_a_stamped_decision_and_fills_only_now_keys"),
    ("this repo routes to a path that is gone",
     "context.toml",
     'path = "docs/charter.md"',
     'path = "docs/charter-moved.md"',
     "tests/test_repo_records.py::test_this_repos_records_pass_lint"),
]

failed = 0
for name, rel, old, new, test in ROWS:
    path = ROOT / rel
    orig = path.read_bytes()
    nl = "\r\n" if b"\r\n" in orig else "\n"  # git may have checked the file out with CRLF
    text = orig.decode("utf-8").replace("\r\n", "\n")
    if old is None:
        lines = text.splitlines(keepends=True)
        broken = "".join(ln for ln in lines if not ln.startswith("body_sha:"))
    else:
        assert old in text, (name, "pattern not found")
        broken = text.replace(old, new, 1)
    assert broken != text, name
    broken = broken.replace("\n", nl)
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
