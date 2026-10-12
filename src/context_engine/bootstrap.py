"""``init``: write the adoption kit into a repo (FRAMEWORK §6.9, §11.4).

The kit is text in ``kit/`` beside this module, shipped as package data, so a plain
``pip install`` of the engine carries it and anyone can read it in the engine repo. ``init``
copies the files a repo is missing and creates the empty record directories. It only ever
creates: an existing file is never touched, except that ``CLAUDE.md`` gets the kit's contract
block appended when the block's markers are not in it yet.

Deliberately not here: installing anything (the engine runs from its own environment and is
never installed into the target repo's), registering the MCP server (a ``claude mcp add`` the
session runs, FRAMEWORK §8.0.2), and committing. ``init`` needs no ``context.toml``, because it
is what writes the first one.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from . import config as C
from .errors import Refusal

KIT = Path(__file__).with_name("kit")
TEMPLATE = "context.toml.template"
CONTRACT = "contract.md"
CONTRACT_TARGET = "CLAUDE.md"
BEGIN, END = "<!-- context-engine kit 0.5 begin -->", "<!-- context-engine kit 0.5 end -->"
# kit file -> where it goes in the repo
FILES = {
    "HANDOFF.md": "HANDOFF.md",
    "docs/charter.md": "docs/charter.md",
    "docs/criteria.md": "docs/criteria.md",
    "docs/ledger/session-log.md": "docs/ledger/session-log.md",
}
KEEP = ("docs/decisions", "docs/stories", "docs/working", "docs/runbooks", "docs/evidence", "tasks")  # empty dirs get a .gitkeep
SELF_IGNORING = (".context", ".scratch")  # each holds a .gitignore of `*`
PREFIX_RE = re.compile(r"^[A-Z][A-Z0-9]*$")


def config_text(prefixes: dict[str, str] | None = None) -> str:
    """The kit's ``context.toml`` with each ``kind=PREFIX`` override applied; refuses one that
    names no kind, is not an upper-case prefix, or collides with another kind's."""
    text = (KIT / TEMPLATE).read_text(encoding="utf-8")
    kinds = tomllib.loads(text)["kinds"]
    for kind, prefix in (prefixes or {}).items():
        if kind not in kinds:
            raise Refusal(f"--prefix names kind {kind!r}, which the kit does not declare", f"use one of {', '.join(kinds)}")
        if not PREFIX_RE.match(prefix):
            raise Refusal(f"prefix {prefix!r} for {kind} is not upper-case letters and digits", "write it like D, DEC or T2")
        section = re.compile(rf"(^\[kinds\.{re.escape(kind)}\]\n(?:(?!\[).*\n)*?prefix = )\"[^\"]*\"", re.MULTILINE)
        text, n = section.subn(lambda m: f'{m.group(1)}"{prefix}"', text, count=1)
        assert n == 1, kind
    C.from_dict(tomllib.loads(text))  # refuses two kinds sharing a prefix
    return text


def plan(root: Path, prefixes: dict[str, str] | None = None) -> tuple[dict[str, str], list[str], list[str]]:
    """(path -> text to write, created, skipped). ``CLAUDE.md``'s text is the whole new file."""
    root = Path(root)
    writes: dict[str, str] = {}
    skipped: list[str] = []
    cfg = config_text(prefixes)
    target = root / C.CONFIG_NAME
    if target.exists():
        if target.read_text(encoding="utf-8").replace("\r\n", "\n") != cfg:
            raise Refusal(
                f"{C.CONFIG_NAME} exists and differs from the kit's",
                "init writes the kit's default layout, which this config may not use: create any missing file by hand "
                "(kit README § Bootstrap by hand), or move context.toml aside and run init again",
            )
        skipped.append(C.CONFIG_NAME)
    else:
        writes[C.CONFIG_NAME] = cfg
    for src, dst in FILES.items():
        if (root / dst).exists():
            skipped.append(dst)
        else:
            writes[dst] = (KIT / src).read_text(encoding="utf-8")
    block = (KIT / CONTRACT).read_text(encoding="utf-8")
    claude = root / CONTRACT_TARGET
    if not claude.exists():
        writes[CONTRACT_TARGET] = f"# {root.resolve().name}: contract\n\n" + block
    else:
        old = claude.read_bytes().decode("utf-8")
        if BEGIN in old:
            skipped.append(CONTRACT_TARGET)
        else:
            norm = old.replace("\r\n", "\n")
            sep = "" if not norm or norm.endswith("\n\n") else ("\n" if norm.endswith("\n") else "\n\n")
            add = sep + block
            writes[CONTRACT_TARGET] = old + (add.replace("\n", "\r\n") if "\r\n" in old else add)
    for d in KEEP:
        if (root / d).exists():
            skipped.append(d + "/")
        else:
            writes[f"{d}/.gitkeep"] = ""
    for d in SELF_IGNORING:
        if (root / d / ".gitignore").exists():
            skipped.append(f"{d}/.gitignore")
        else:
            writes[f"{d}/.gitignore"] = "*\n"
    return writes, list(writes), skipped


def init(root: Path | str, prefixes: dict[str, str] | None = None, dry_run: bool = False) -> str:
    """Write what the repo is missing; return one line naming what was created and skipped."""
    root = Path(root)
    if not root.is_dir():
        raise Refusal(f"{root} is not a directory", "pass the repo root with --root")
    writes, created, skipped = plan(root, prefixes)
    if not dry_run:
        for rel, text in writes.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)
    verb = "would create" if dry_run else "created"
    head = "init (dry run)" if dry_run else "init"
    nxt = "" if dry_run or not created else "; next: fill docs/charter.md with the owner, register the MCP server, run lint"
    return f"{head}: {verb} {len(created)} ({', '.join(created) or 'none'}); skipped {len(skipped)} ({', '.join(skipped) or 'none'}){nxt}"
