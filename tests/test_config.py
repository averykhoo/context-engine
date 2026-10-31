"""The config's guard ids (config.py::LINT_IDS): every id a lint failure can carry is one
`[guards] off` may name and `coverage` reads as built (CE-6, AC-168)."""

import re
from pathlib import Path

import pytest

import context_engine
from context_engine.config import LINT_IDS, from_dict

from test_working import CONFIG

FAILURE_ID_RE = re.compile(r"""\bFailure\(\s*["']([A-Za-z][\w-]*)["']""")


def _emitted() -> dict[str, str]:
    """Each guard id a `Failure("<id>", ...)` in the engine's source names, with the first file naming it."""
    found: dict[str, str] = {}
    for p in sorted(Path(context_engine.__file__).parent.glob("*.py")):
        for m in FAILURE_ID_RE.finditer(p.read_text(encoding="utf-8")):
            found.setdefault(m[1], p.name)
    return found


@pytest.mark.criterion("AC-168")
def test_every_guard_id_a_lint_failure_carries_is_in_lint_ids():
    found = _emitted()
    assert {"G-D0", "G-W7", "G-W9"} <= set(found), sorted(found)  # the scan finds what it must, so an empty one cannot pass
    missing = {i: f for i, f in found.items() if i not in LINT_IDS}
    assert not missing, f"lint can report {missing}, which config.LINT_IDS lacks: `[guards] off` cannot name them and coverage misreads them"
    for gid in found:
        assert from_dict({**CONFIG, "guards": {"off": [gid]}}).guards.off == (gid,)  # `[guards] off` takes each one
