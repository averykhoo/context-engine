"""The MCP server: one tool per operation in ``ops.OPS``, over stdio (FRAMEWORK §8.0.2, CE-3).

``python -m context_engine.mcp [--root DIR]``; the root defaults to the working directory,
which Claude Code sets to the project it started in. Agents see the tools as
``mcp__context-engine__<name>``.

Each tool calls its operation's function, the same one the CLI calls (AC-18): this module only
adds the caller and caps the reads. A write returns its one line; a read longer than
``read_max_bytes`` is cut at a line and says where the rest is (AC-19). A refusal comes back as
a tool error carrying its remedy.

**The caller.** A server process is not a framework session (§8.0.2): it can outlive a
``/clear``. ``session_start`` remembers the key it minted and the actor it was given, and every
later tool uses them unless it is passed ``session`` or ``actor`` itself (a subagent passes its
own ``actor``). Before any ``session_start``, ``CE_SESSION`` and ``CE_ACTOR`` are the fallback.

Deliberately not here: the ``hk_`` operations other than ``hk_expire_batons`` (CE-6), and any
judgement: a tool carries out what the caller decided.
"""

from __future__ import annotations

import argparse
import inspect
import os
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import ops
from .errors import Refusal
from .working import Engine

NAME = "context-engine"  # DEC-15
INSTRUCTIONS = (
    "Records and working state for this repo. Start every session with session_start(actor=...), "
    "then orient. Writes return one line; reads are capped and say where the rest is."
)


def cap(text: str, limit: int, rest: str) -> str:
    """``text`` if it fits in ``limit`` bytes, else whole lines up to it plus where the rest is."""
    if len(text.encode()) <= limit:
        return text
    lines = text.splitlines(keepends=True)
    note = f"\n[cut at {limit} bytes, {{shown}} of {len(lines)} lines; the rest: {rest}]"
    budget = limit - len(note.encode()) - 8  # room for the line count
    keep, size = [], 0
    for line in lines:
        if size + len(line.encode()) > budget:
            break
        keep.append(line)
        size += len(line.encode())
    return "".join(keep).rstrip("\n") + note.format(shown=len(keep))


def _caller_params(o: ops.Op) -> list[inspect.Parameter]:
    kw = inspect.Parameter.KEYWORD_ONLY
    extra = [inspect.Parameter("session", kw, default=None, annotation=str | None)] if o.name != "session_start" else []
    if o.write:
        actor = inspect.Parameter("actor", kw, default=None, annotation=str | None)
        extra.append(actor)
    return extra


def make_tool(o: ops.Op, root: Path, state: ops.Caller):
    """A function with the operation's own parameters plus ``session``/``actor``, for the SDK to
    build the tool's schema from."""

    def tool(**kw: Any) -> str:
        c = ops.Caller(kw.pop("session", None) or state.session, kw.pop("actor", None) or state.actor)
        try:
            e = Engine(root)
            _, text = o.fn(e, c, **kw)
        except Refusal as r:
            raise ToolError(str(r)) from r  # the SDK passes a ToolError's text, remedy and all, to the agent
        if o.name == "session_start":
            state.session, state.actor = c.session, c.actor
        return text if o.write or o.name == "orient" else cap(text, e.w.read_max_bytes, o.rest)

    params = [p.replace(kind=inspect.Parameter.KEYWORD_ONLY) for p in o.params] + _caller_params(o)
    tool.__signature__ = inspect.Signature(params, return_annotation=str)
    tool.__annotations__ = {p.name: p.annotation for p in params} | {"return": str}
    tool.__name__ = o.name
    tool.__doc__ = o.fn.__doc__
    return tool


def server(root: Path | str = ".") -> MCPServer:
    root = Path(root).resolve()
    state = ops.Caller(os.environ.get("CE_SESSION"), os.environ.get("CE_ACTOR"))
    s = MCPServer(name=NAME, instructions=INSTRUCTIONS)
    for o in ops.OPS.values():
        s.add_tool(make_tool(o, root, state), name=o.name)
    return s


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m context_engine.mcp")
    ap.add_argument("--root", default=".", help="the repo root (default: the working directory)")
    server(ap.parse_args(argv).root).run("stdio")


if __name__ == "__main__":
    main()
