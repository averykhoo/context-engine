"""CI's gate job (.github/workflows/gate.yml) on a commit, in a Linux container on this machine
(CE-67, US-18). The owner works on Windows and CI runs on Linux: a test that leans on Windows
behaviour, or on the machine's git config, is green here and red there, and the push finds out
(39e09ca: three such tests; docs/evidence/ci-divergence-2026-10-13.md).

The container is set up like CI's runner: `ubuntu-latest`'s release, git from the git-core PPA
with `safe.directory = *` in `/etc/gitconfig` as the runner image installs it, the runner's uid,
Python at the `requires-python` floor. It does what the workflow does: a fresh clone of exactly
that commit (so `core.autocrlf` and untracked files cannot leak in), `pip install -e ".[dev]"`,
then the gate. It prints the git and Python versions it ran with: CI's git moves with its PPA, so
compare them with the CI log's when the two disagree.

Usage: <interpreter> tools/linux_gate.py [rev]   (default HEAD; the commit need not be pushed)
Needs docker: on Windows through WSL (`wsl docker`, the engine in the default distro), elsewhere
`docker` on PATH. The image is built once and cached. Exit status is the gate's; the full log is
.scratch/linux-gate/<sha>.log. tests/test_ci.py keeps the steps in step with the workflow."""
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = 'python -m pip install -q -e ".[dev]"'  # the workflow's Install step, quieter
GATE = "python -m pytest -q"  # the workflow's Gate step
RUNNER = "ubuntu:24.04"  # what `ubuntu-latest` is on 2026-10-13; move it when GitHub does


def floor() -> str:
    spec = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["requires-python"]
    return spec.removeprefix(">=").strip()


def dockerfile(py: str) -> str:
    return "\n".join([
        f"FROM {RUNNER}",
        "RUN apt-get update -qq"
        " && apt-get install -y -qq --no-install-recommends software-properties-common gpg-agent >/dev/null"
        " && add-apt-repository -y ppa:git-core/ppa >/dev/null"
        f" && apt-get install -y -qq --no-install-recommends git python{py} python{py}-venv >/dev/null"
        " && rm -rf /var/lib/apt/lists/* && useradd -m -u 1001 runner"
        # as the runner image's install-git.sh does (actions/checkout#760): git trusts every directory
        " && printf '[safe]\\n\\tdirectory = *\\n' >> /etc/gitconfig",
        "USER runner",
        "WORKDIR /home/runner",
        "",
    ])


def script(sha: str, py: str) -> str:
    return " && ".join([
        "git --version", f"python{py} --version",
        "git clone -q --no-checkout /src w", "cd w",  # /src is another uid's: the system config trusts it
        f"git -c advice.detachedHead=false checkout -q {sha}",
        f"python{py} -m venv ../venv", ". ../venv/bin/activate",
        INSTALL, GATE,
    ])


def main(argv: list[str]) -> int:
    rev = argv[0] if argv else "HEAD"
    sha = subprocess.run(["git", "rev-parse", "--verify", rev + "^{commit}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    py = floor()
    tag = f"context-engine-linux-gate:{RUNNER.replace(':', '-')}-py{py}"
    if sys.platform == "win32":
        docker = ["wsl", "-e", "docker"]
        src = subprocess.run(["wsl", "-e", "wslpath", "-a", ROOT.as_posix()], capture_output=True, text=True, check=True).stdout.strip()
    else:
        docker, src = ["docker"], str(ROOT)
    subprocess.run([*docker, "build", "-q", "-t", tag, "-"], input=dockerfile(py), text=True, check=True, stdout=subprocess.DEVNULL)
    log = ROOT / ".scratch" / "linux-gate" / f"{sha}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    print(f"linux gate: {sha[:12]} on {tag}; log {log.relative_to(ROOT).as_posix()}", flush=True)
    with log.open("w", encoding="utf-8") as out:
        rc = subprocess.run([*docker, "run", "--rm", "--name", f"linux-gate-{sha[:12]}", "-v", f"{src}:/src:ro", tag, "sh", "-c", script(sha, py)],
                            stdout=out, stderr=subprocess.STDOUT).returncode
    lines = log.read_text(encoding="utf-8").splitlines()
    print("\n".join([ln for ln in lines if ln.startswith(("git version", "Python ", "FAILED", "ERROR", "fatal:"))] + lines[-1:]))
    print(f"linux gate: {'green' if rc == 0 else f'RED (exit {rc})'} on {sha[:12]}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
