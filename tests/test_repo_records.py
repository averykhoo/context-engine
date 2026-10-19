"""This repo's own records, read through its own context.toml (dogfood, CE-8)."""

from pathlib import Path

import pytest

from context_engine.config import load
from context_engine.working import Engine

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.criterion("AC-23")
def test_this_repos_records_pass_lint():
    """Every record parses and fits its schema, every decision and story is stamped and still
    matches its stamp (G-D10), and the working state passes its guards (G-W1 to G-W6)."""
    assert [str(f) for f in Engine(REPO).lint()] == []


# This repo switches no guard off (CE-52). Lint drops every id `[guards] off` names, so a guard
# added there is silenced with lint green: a silent false green. Turning one off takes an owner
# decision (a DEC-n record); the change that follows it edits this pin and cites that decision.
OFF_PINNED: tuple[str, ...] = ()


def test_this_repos_guards_off_list_is_pinned():
    """The `[guards] off` list the engine reads from this repo's context.toml is the pinned one."""
    off = load(REPO).guards.off
    assert off == OFF_PINNED, (
        f"context.toml [guards] off is {list(off)}, pinned {list(OFF_PINNED)}: switching a guard off "
        "needs an owner decision (DEC-n); record it, then update OFF_PINNED here citing it")
