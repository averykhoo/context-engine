"""The CI workflow runs exactly the gate, at the declared Python floor, on every push (CE-10)."""

import re
import tomllib
from pathlib import Path

from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "gate.yml"


def _workflow() -> dict:
    return YAML(typ="safe").load(WORKFLOW.read_text(encoding="utf-8"))


def _pyproject() -> dict:
    return tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))


def _name(req: str) -> str:
    return re.match(r"[A-Za-z0-9_.-]+", req.strip()).group(0).lower().replace("_", "-")


def _steps() -> list[dict]:
    (job,) = _workflow()["jobs"].values()
    return job["steps"]


def test_the_workflow_runs_on_every_push_with_no_paths_filter():
    on = _workflow()["on"]  # YAML 1.2: `on` is a string key, not true
    assert "push" in on, on
    push = on["push"] or {}
    assert not {"paths", "paths-ignore", "branches", "branches-ignore"} & set(push), (
        "docs/, tasks/ and context.toml are records lint checks: a filtered push can skip a red gate"
    )


def test_the_workflow_python_is_the_declared_floor():
    floor = re.fullmatch(r">=\s*(\d+\.\d+)", _pyproject()["project"]["requires-python"].strip()).group(1)
    pythons = [s["with"]["python-version"] for s in _steps() if str(s.get("uses", "")).startswith("actions/setup-python@")]
    assert pythons == [floor], pythons


def test_the_workflow_installs_dev_and_runs_exactly_the_gate():
    gate_section = (REPO / "CLAUDE.md").read_text(encoding="utf-8").split("\n## Gate\n", 1)[1]
    gate = re.search(r"`([^`]+)`", gate_section).group(1).replace("<interpreter>", "python")
    runs = [s["run"].strip() for s in _steps() if "run" in s]
    assert runs == ['python -m pip install -e ".[dev]"', gate], runs


def test_the_dev_extra_carries_the_build_system_requires():
    """test_kit builds the wheel with --no-build-isolation, so a clean `.[dev]` install must bring
    the build backend itself (Python 3.12 environments ship without setuptools)."""
    data = _pyproject()
    dev = {_name(r) for r in data["project"]["optional-dependencies"]["dev"]}
    build = {_name(r) for r in data["build-system"]["requires"]}
    assert build - dev == set(), f"missing from [dev]: {sorted(build - dev)}"
