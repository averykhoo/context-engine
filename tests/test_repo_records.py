"""This repo's own records, read through its own context.toml (dogfood, CE-8)."""

from pathlib import Path

import pytest

from context_engine.working import Engine

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.criterion("AC-23")
def test_this_repos_records_pass_lint():
    """Every record parses and fits its schema, every decision and story is stamped and still
    matches its stamp (G-D10), and the working state passes its guards (G-W1 to G-W6)."""
    assert [str(f) for f in Engine(REPO).lint()] == []
