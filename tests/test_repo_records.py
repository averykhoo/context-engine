"""This repo's own hand-written records, read through its own context.toml (dogfood, CE-8)."""

from pathlib import Path

from context_engine.store import Store

REPO = Path(__file__).resolve().parents[1]


def test_this_repos_records_pass_every_check_except_the_body_stamp():
    """Every record parses and fits its schema. Stamping body_sha is CE-8's job, so G-D10 is
    the one failure allowed here, and only the "no body_sha" kind of it."""
    failures = Store(REPO).lint()
    other = [str(f) for f in failures if not (f.guard == "G-D10" and "no body_sha" in f.message)]
    assert other == []
