"""A test's result does not depend on the machine it runs on (CE-67, US-18): the owner's Windows
checkout and CI's Linux runner run the same gate. The failures these guard against, and how each
was found, are in docs/evidence/ci-divergence-2026-10-13.md."""

import re
import subprocess
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
STDLIB = r"(?:time|os|subprocess|sys|shutil|tempfile|socket|signal|threading)"
PATCH = re.compile(rf"setattr\(\s*(?:\w+\.)?{STDLIB}\s*,|setattr\(\s*[\"']{STDLIB}\.")


@pytest.mark.criterion("AC-80")
def test_no_test_patches_an_attribute_of_a_standard_library_module():
    """Patching `time.sleep` patches it for the standard library too, and what the standard library
    does with it differs by platform (on Linux `subprocess` waits with it; on Windows it does not).
    Patch the engine module's own name for it instead: `setattr(C, "time", <stand-in>)`."""
    hits = [f"{p.name}:{n}: {ln.strip()}" for p in sorted(TESTS.glob("*.py")) if p.name != Path(__file__).name
            for n, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if PATCH.search(ln)]
    assert hits == [], "\n".join(hits)


@pytest.mark.criterion("AC-80")
def test_git_in_a_test_reads_no_system_or_global_config(tmp_path):
    """conftest's `_no_machine_git_config`: CI's `/etc/gitconfig` trusts every directory and Git for
    Windows' sets `core.autocrlf`; a test sees neither."""
    p = subprocess.run(["git", "config", "--list", "--show-scope"], cwd=tmp_path, capture_output=True, text=True)
    scopes = {ln.split("\t", 1)[0] for ln in p.stdout.splitlines() if ln.strip()}
    assert scopes <= {"command", "local", "worktree"}, p.stdout
