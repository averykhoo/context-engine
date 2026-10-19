"""`context-engine --help` describes every group, operation and option (CE-72): a new user learns
`session close` or `task new` from the CLI itself, not only from the runbook."""

import argparse

from context_engine.cli import build


def _walk(parser: argparse.ArgumentParser, name: str):
    """(spelling, parser) for the parser and every parser under it."""
    yield name, parser
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for sub, sp in action.choices.items():
                yield from _walk(sp, f"{name} {sub}")


def _undocumented() -> list[str]:
    missing = []
    for name, parser in _walk(build(), "context-engine"):
        if not (parser.description or "").strip():
            missing.append(f"`{name} --help` has no description")
        for action in parser._actions:
            if isinstance(action, argparse._HelpAction):
                continue
            if isinstance(action, argparse._SubParsersAction):
                listed = {a.dest: (a.help or "").strip() for a in action._choices_actions}
                missing += [f"`{name}` lists `{sub}` without a help line" for sub in action.choices if not listed.get(sub)]
                continue
            if not (action.help or "").strip() or action.help == argparse.SUPPRESS:
                missing.append(f"`{name}` {'/'.join(action.option_strings) or action.dest} has no help")
    return missing


def test_every_group_operation_and_option_has_help():
    assert _undocumented() == []


def test_the_walk_reaches_every_operation_and_option():
    """The check above is only as good as its walk: it must see the nested operations and their
    arguments, not just the top level."""
    seen = dict(_walk(build(), "context-engine"))
    assert {"context-engine session close", "context-engine task new", "context-engine banner set"} <= set(seen)
    close = {s for a in seen["context-engine session close"]._actions for s in a.option_strings}
    assert {"--rows", "--summary", "--guards", "--read", "--asked", "--owed"} <= close


def test_every_help_renders():
    """Every parser's --help formats without error (a stray `%` in a help string breaks it)."""
    for name, parser in _walk(build(), "context-engine"):
        assert parser.format_help(), name
