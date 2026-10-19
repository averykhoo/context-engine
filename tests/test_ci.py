"""The CI workflow runs exactly the gate, at the declared Python floor, on every push (CE-10)."""

import importlib.util
import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from types import SimpleNamespace

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


def _linux_gate():
    spec = importlib.util.spec_from_file_location("linux_gate", REPO / "tools" / "linux_gate.py")
    lg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lg)
    return lg


def _git(cwd, *args):
    p = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false", *args],
                       cwd=cwd, capture_output=True, text=True)
    assert p.returncode == 0, (args, p.returncode, p.stderr)
    return p.stdout.strip()


def _repo_and_worktree(tmp_path):
    """A plain repository and a worktree of it, the worktree holding a commit on no branch (CE-86)."""
    host = tmp_path / "host"
    main, wt = host / "repo", host / "wt"
    main.mkdir(parents=True)
    _git(main, "init", "-q", "-b", "main")
    (main / "f.txt").write_text("main\n", encoding="utf-8")
    _git(main, "add", "f.txt")
    _git(main, "commit", "-q", "-m", "main")
    _git(main, "worktree", "add", "-q", "--detach", str(wt))
    (wt / "f.txt").write_text("worktree only\n", encoding="utf-8")
    _git(wt, "commit", "-q", "-am", "in the worktree, on no branch")
    return host, main, wt


def test_the_local_linux_gate_mounts_a_git_dir_a_worktree_s_commit_can_be_cloned_from(tmp_path):
    """CE-86: run from a git worktree, tools/linux_gate.py mounted the checkout, whose `.git` file
    names a host path the container does not have, so `git clone /src` exited 128. What it mounts
    must clone on its own: here the mount is a copy of `source()`, and the host repo is moved away
    before the clone, as it is absent in the container. The worktree's commit exists only there. A
    plain clone works as before, and its `source()` is absolute: a relative `.git` would be mounted
    from the caller's directory, not the repository's."""
    lg = _linux_gate()
    host, main, wt = _repo_and_worktree(tmp_path)
    plain = lg.source(main)
    assert plain.is_absolute() and plain.samefile(main / ".git"), plain
    cases = {"wt": (wt, "worktree only\n"), "main": (main, "main\n")}
    shas = {}
    for name, (root, _) in cases.items():
        shutil.copytree(lg.source(root), tmp_path / f"src-{name}")  # docker run -v <source>:/src:ro
        shas[name] = _git(root, "rev-parse", "HEAD")
    host.rename(tmp_path / "gone")  # the container has none of the host's paths
    for name, (_, text) in cases.items():
        w = tmp_path / f"w-{name}"
        _git(tmp_path, "clone", "-q", "--no-checkout", str(tmp_path / f"src-{name}"), w.name)  # the script's two git steps
        _git(w, "-c", "advice.detachedHead=false", "checkout", "-q", shas[name])
        assert (w / "f.txt").read_text(encoding="utf-8") == text, name


@pytest.mark.parametrize("platform", ["linux", "win32"])
def test_the_local_linux_gate_s_docker_run_mounts_what_source_returns(tmp_path, monkeypatch, platform):
    """CE-86: `main` must mount `source(ROOT)`, not ROOT, on both of its branches (through
    `wslpath` on Windows, the path itself elsewhere). Run here from a worktree, with every wsl and
    docker call recorded instead of run; git runs for real."""
    lg = _linux_gate()
    _, _, wt = _repo_and_worktree(tmp_path)
    monkeypatch.setattr(lg, "ROOT", wt)
    monkeypatch.setattr(lg, "floor", lambda: "3.12")
    calls = []

    def run(cmd, *args, **kwargs):
        if cmd[0] == "git":
            return subprocess.run(cmd, *args, **kwargs)
        calls.append(cmd)
        out = "/wsl/" + cmd[-1] if cmd[:4] == ["wsl", "-e", "wslpath", "-a"] else ""
        return subprocess.CompletedProcess(cmd, 0, stdout=out, stderr="")

    # the module's own names, not the standard library's (tests/test_portability.py, AC-80)
    monkeypatch.setattr(lg, "sys", SimpleNamespace(platform=platform))
    monkeypatch.setattr(lg, "subprocess", SimpleNamespace(run=run, DEVNULL=subprocess.DEVNULL, STDOUT=subprocess.STDOUT))
    assert lg.main([]) == 0
    gitdir = lg.source(wt)
    assert not gitdir.samefile(wt), gitdir
    (docker_run,) = [c for c in calls if "-v" in c]
    mount = docker_run[docker_run.index("-v") + 1]
    if platform == "win32":
        (wslpath,) = [c for c in calls if "wslpath" in c]
        assert wslpath[-1] == gitdir.as_posix(), wslpath
        assert mount == f"/wsl/{gitdir.as_posix()}:/src:ro", mount
    else:
        assert mount == f"{gitdir}:/src:ro", mount
    assert docker_run[-1] == lg.script(_git(wt, "rev-parse", "HEAD"), "3.12"), docker_run


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


def test_the_procedures_runbook_gives_ci_s_by_hand_fallback_and_the_contract_names_the_workflow():
    """Every programmatic process has its by-hand fallback in a runbook: CI's is the same install
    and gate in a fresh environment, in procedures.md § Push and CI."""
    procedures = (REPO / "docs" / "runbooks" / "procedures.md").read_text(encoding="utf-8")
    push = procedures.split("\n## Push and CI (§6.8)\n", 1)[1].split("\n## ", 1)[0]
    (install,) = [s["run"].strip().removeprefix("python -m ") for s in _steps() if "pip install" in s.get("run", "")]
    rows = [ln.split("|") for ln in push.splitlines() if ln.startswith("|") and install in ln]
    assert len(rows) == 1, "procedures.md § Push and CI needs one step giving CI's install by hand"
    by_hand = rows[0][4]  # `| § | Do | Engine | By hand | Why |`
    for part in (install, "fresh environment", "requires-python", "<gate>"):
        assert part in by_hand, f"the by-hand fallback lacks {part!r}: {by_hand}"
    gate_section = (REPO / "CLAUDE.md").read_text(encoding="utf-8").split("\n## Gate\n", 1)[1].split("\n## ", 1)[0]
    assert WORKFLOW.relative_to(REPO).as_posix() in gate_section, "CLAUDE.md § Gate does not name the CI workflow"
