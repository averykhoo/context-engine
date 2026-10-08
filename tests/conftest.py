import subprocess
import sys
import time
from pathlib import Path

import pytest

from context_engine.store import Store

REPO = Path(__file__).resolve().parents[1]
SESSION = "2026-10-08c"
ACTOR = "claude-code/test"
WORKER = Path(__file__).with_name("_worker.py")

CONFIG = {
    "engine": {"oplog": "ops.jsonl", "lockfile": ".context/engine.lock", "bundles": ["docs/decisions", "tasks"]},
    "kinds": {
        "decision": {
            "type": "Decision",
            "prefix": "DEC",
            "dir": "docs/decisions",
            "mode": "append-only",
            "required": ["title", "decision_status"],
            "enums": {"decision_status": ["BUILT", "PROVISIONAL", "DEFERRED", "SUPERSEDED", "REJECTED"]},
        },
        "task": {
            "type": "Task",
            "prefix": "CE",
            "dir": "tasks",
            "mode": "replaced",
            "required": ["title", "pri", "state"],
            "enums": {"pri": ["NOW", "NEXT", "LATER", "SOMEDAY"], "state": ["open", "closed"]},
            "extra_dirs": ["tasks/closed"],
        },
    },
}


@pytest.fixture
def repo(tmp_path):
    """An empty target repo with a context.toml; returns a Store on it."""
    (tmp_path / "context.toml").write_text(_toml(CONFIG), encoding="utf-8")
    return Store(tmp_path)


def _toml(d, prefix=""):
    """Just enough TOML for CONFIG (tables, strings, lists, inline tables of lists)."""
    out, tables = [], []
    for k, v in d.items():
        if isinstance(v, dict) and not (prefix and k == "enums"):
            tables.append((k, v))
        else:
            out.append(f"{k} = {_val(v)}")
    text = "\n".join(out) + "\n"
    for k, v in tables:
        name = f"{prefix}.{k}" if prefix else k
        text += f"[{name}]\n" + _toml(v, name)
    return text


def _val(v):
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, list):
        return "[" + ", ".join(_val(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_val(x)}" for k, x in v.items()) + " }"
    return str(v)


def run_workers(root: Path, jobs: list[list[str]]) -> None:
    """Start one OS process per job, release them together, and require every one to succeed."""
    gate = root / "go"
    procs = [
        subprocess.Popen([sys.executable, str(WORKER), str(root), str(gate), *job], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for job in jobs
    ]
    time.sleep(0.5)  # let every process import and reach the gate
    gate.write_text("go")
    for p in procs:
        out, _ = p.communicate(timeout=120)
        assert p.returncode == 0, out


@pytest.fixture
def workers():
    return run_workers
