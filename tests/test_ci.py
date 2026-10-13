"""The CI workflow runs exactly the gate, at the declared Python floor, on every push (CE-10)."""

import importlib.util
import re
import tomllib
from pathlib import Path

import pytest
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


@pytest.mark.criterion("AC-79")
def test_the_local_linux_gate_runs_the_workflow_s_steps_on_its_runner_s_shape():
    """tools/linux_gate.py (CE-67) is CI's job on this machine: the same two steps, the floor's
    Python, an Ubuntu image for `ubuntu-latest`, and the runner image's `safe.directory = *`."""
    spec = importlib.util.spec_from_file_location("linux_gate", REPO / "tools" / "linux_gate.py")
    lg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lg)
    runs = [s["run"].strip() for s in _steps() if "run" in s]
    assert [lg.INSTALL.replace(" -q", ""), lg.GATE] == runs
    (job,) = _workflow()["jobs"].values()
    assert job["runs-on"] == "ubuntu-latest" and lg.RUNNER.startswith("ubuntu:"), (job["runs-on"], lg.RUNNER)
    floor = re.fullmatch(r">=\s*(\d+\.\d+)", _pyproject()["project"]["requires-python"].strip()).group(1)
    assert lg.floor() == floor
    image, script = lg.dockerfile(floor), lg.script("0" * 40, floor)
    assert "ppa:git-core/ppa" in image and "directory = *" in image and "-u 1001" in image, image
    assert script.index("clone") < script.index("checkout -q " + "0" * 40) < script.index(lg.INSTALL) < script.index(lg.GATE), script


def test_the_dev_extra_carries_the_build_system_requires():
    """test_kit builds the wheel with --no-build-isolation, so a clean `.[dev]` install must bring
    the build backend itself (Python 3.12 environments ship without setuptools)."""
    data = _pyproject()
    dev = {_name(r) for r in data["project"]["optional-dependencies"]["dev"]}
    build = {_name(r) for r in data["build-system"]["requires"]}
    assert build - dev == set(), f"missing from [dev]: {sorted(build - dev)}"


def test_nothing_in_the_workflow_can_skip_or_mask_the_gate():
    """`if:` can skip the job or a step and `continue-on-error:` turns a red step green: either
    leaves a CI run that can never go red."""
    (job,) = _workflow()["jobs"].values()
    masks = {"if", "continue-on-error"}
    found = [("job", k) for k in masks & set(job)]
    found += [(s.get("name") or s.get("uses") or s.get("run"), k) for s in job["steps"] for k in masks & set(s)]
    assert found == [], found


def test_the_rituals_runbook_gives_ci_s_by_hand_fallback_and_the_contract_names_the_workflow():
    """Every programmatic process has its by-hand fallback in a runbook: CI's is the same install
    and gate in a fresh environment, in rituals.md § Push and CI."""
    rituals = (REPO / "docs" / "runbooks" / "rituals.md").read_text(encoding="utf-8")
    push = rituals.split("\n## Push and CI (§6.8)\n", 1)[1].split("\n## ", 1)[0]
    (install,) = [s["run"].strip().removeprefix("python -m ") for s in _steps() if "pip install" in s.get("run", "")]
    rows = [ln.split("|") for ln in push.splitlines() if ln.startswith("|") and install in ln]
    assert len(rows) == 1, "rituals.md § Push and CI needs one step giving CI's install by hand"
    by_hand = rows[0][4]  # `| § | Do | Engine | By hand | Why |`
    for part in (install, "fresh environment", "requires-python", "<gate>"):
        assert part in by_hand, f"the by-hand fallback lacks {part!r}: {by_hand}"
    gate_section = (REPO / "CLAUDE.md").read_text(encoding="utf-8").split("\n## Gate\n", 1)[1].split("\n## ", 1)[0]
    assert WORKFLOW.relative_to(REPO).as_posix() in gate_section, "CLAUDE.md § Gate does not name the CI workflow"
