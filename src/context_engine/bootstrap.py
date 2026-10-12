"""``init``: write the adoption kit into a repo (FRAMEWORK §6.9, §11.4).

The kit is text in ``kit/`` beside this module, shipped as package data, so a plain
``pip install`` of the engine carries it and anyone can read it in the engine repo. ``init``
copies the files a repo is missing and creates the empty record directories. It only ever
creates: an existing file is never touched, except that ``CLAUDE.md`` gets the kit's contract
block appended when no kit block (of any version) is in it yet. An existing ``context.toml`` is
kept, so init can be re-run after it is edited to fill in what is still missing.

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
# any kit version's begin marker: an older block is the one an upgrade replaces, never a second one
ANY_BEGIN = re.compile(r"<!-- context-engine kit (\S+) begin -->")
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


def _existing_config(root: Path, prefixes: dict[str, str] | None) -> C.Config:
    """The repo's own ``context.toml``, which init keeps: it must load, and agree with any
    ``--prefix`` given (init never edits a config, so a different prefix is edited by hand)."""
    try:
        cfg = C.load(root)
    except Refusal as e:
        raise Refusal(f"{C.CONFIG_NAME} exists and does not load: {e.message}", e.remedy + "; then run init again") from None
    except ValueError as e:  # tomllib.TOMLDecodeError
        raise Refusal(f"{C.CONFIG_NAME} exists and is not TOML: {e}", "fix it, then run init again") from None
    for kind, prefix in (prefixes or {}).items():
        have = cfg.kinds[kind].prefix if kind in cfg.kinds else None
        if have != prefix:
            raise Refusal(
                f"{C.CONFIG_NAME} exists and gives {kind} the prefix {have!r}, not {prefix!r}",
                f"init never edits a config: change `prefix` in [kinds.{kind}] by hand, or run init without --prefix",
            )
    return cfg


def _uses(cfg: C.Config) -> set[str]:
    """Every repo path the config points at: kind dirs, working files, routes, the lock and op log."""
    w = cfg.working
    paths = [k.dir for k in cfg.kinds.values()] + [r.path for r in cfg.routes] + [cfg.lockfile, cfg.oplog, w.ledger, w.handoff, w.register]
    return {p.strip("/") for p in paths if p}


def _used(rel: str, uses: set[str]) -> bool:
    return any(u == rel or u.startswith(rel + "/") or rel.startswith(u + "/") for u in uses)


def plan(root: Path, prefixes: dict[str, str] | None = None) -> tuple[dict[str, str], list[str], list[str]]:
    """(path -> text to write, created, skipped). ``CLAUDE.md``'s text is the whole new file.

    A ``context.toml`` already present is kept, once it loads, and a skeleton or directory is then
    written only where that config points: a repo that mapped a component elsewhere (§11.4) does
    not get the kit's default file back on a re-run."""
    root = Path(root)
    writes: dict[str, str] = {}
    skipped: list[str] = []
    text = config_text(prefixes)
    if (root / C.CONFIG_NAME).exists():
        cfg = _existing_config(root, prefixes)
        skipped.append(C.CONFIG_NAME)
    else:
        cfg = C.from_dict(tomllib.loads(text))
        writes[C.CONFIG_NAME] = text
    uses = _uses(cfg)
    for src, dst in FILES.items():
        if not _used(dst, uses):
            skipped.append(f"{dst} (not in {C.CONFIG_NAME})")
        elif (root / dst).exists():
            skipped.append(dst)
        else:
            writes[dst] = (KIT / src).read_text(encoding="utf-8")
    block = (KIT / CONTRACT).read_text(encoding="utf-8")
    claude = root / CONTRACT_TARGET
    if not claude.exists():
        writes[CONTRACT_TARGET] = f"# {root.resolve().name}: contract\n\n" + block
    else:
        old = claude.read_bytes().decode("utf-8")
        have = ANY_BEGIN.search(old)
        if have and have.group(0) == BEGIN:
            skipped.append(CONTRACT_TARGET)
        elif have:  # never a second block beside an older one: the upgrade replaces it (kit README § Upgrade)
            skipped.append(f"{CONTRACT_TARGET} (holds the kit {have.group(1)} block: replace it with kit/{CONTRACT} by hand)")
        else:
            norm = old.replace("\r\n", "\n")
            sep = "" if not norm or norm.endswith("\n\n") else ("\n" if norm.endswith("\n") else "\n\n")
            add = sep + block
            writes[CONTRACT_TARGET] = old + (add.replace("\n", "\r\n") if "\r\n" in old else add)
    for d in KEEP:
        if not _used(d, uses):
            skipped.append(f"{d}/ (not in {C.CONFIG_NAME})")
        elif (root / d).exists():
            skipped.append(d + "/")
        else:
            writes[f"{d}/.gitkeep"] = ""
    for d in SELF_IGNORING:
        if not _used(d, uses):
            skipped.append(f"{d}/ (not in {C.CONFIG_NAME})")
        elif (root / d / ".gitignore").exists():
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
