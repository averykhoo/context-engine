"""The manual-mode runbook covers every engine operation, each with its reason (US-11)."""

import argparse
import re
from pathlib import Path

import pytest

from context_engine.cli import build

RUNBOOK = Path(__file__).resolve().parents[1] / "docs" / "runbooks" / "manual-mode.md"


def _subparsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


def cli_operations() -> list[str]:
    """Every `context-engine <group> [<op>]` the CLI accepts, read from the parser itself."""
    ops = []
    for group, gp in _subparsers(build()).items():
        subs = _subparsers(gp)
        ops += [f"context-engine {group} {op}" for op in subs] if subs else [f"context-engine {group}"]
    return ops


def runbook_sections() -> dict[str, str]:
    """`### <heading>` -> its text up to the next heading."""
    text = RUNBOOK.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = re.sub(r"^[ \t]*```.*?^[ \t]*```", "", text, flags=re.MULTILINE | re.DOTALL)  # a `## ` in an example is not a heading
    parts = re.split(r"^(#{2,3} .*)$", text, flags=re.MULTILINE)
    return {parts[i][4:].strip(): parts[i + 1] for i in range(1, len(parts), 2) if parts[i].startswith("### ")}


@pytest.mark.criterion("AC-21")
def test_every_cli_operation_has_a_runbook_section_with_its_reason():
    sections = runbook_sections()
    ops = cli_operations()
    assert len(ops) >= 25, ops  # the parser walk itself must not silently find nothing
    missing = [op for op in ops if op not in sections]
    assert missing == [], f"no `### <op>` section in {RUNBOOK.name} for: {missing}"
    no_why = [op for op in ops if "**Why:**" not in sections[op]]
    assert no_why == [], f"sections without a **Why:** line: {no_why}"
