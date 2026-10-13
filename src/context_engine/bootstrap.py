"""``init``: write the adoption kit into a repo (FRAMEWORK §6.9, §11.4).

The kit is text in ``kit/`` beside this module, shipped as package data, so a plain
``pip install`` of the engine carries it and anyone can read it in the engine repo. ``init``
copies the files a repo is missing and creates the empty record directories. It only ever
creates: an existing file is never touched, except that ``CLAUDE.md`` gets the kit's bootloader
appended when no kit block (of any version) is in it yet. An existing ``context.toml`` is kept,
so init can be re-run after it is edited to fill in what is still missing.

The bootloader (CE-38, US-17) is a few lines between the kit markers: the ``framework:`` pin and
an ``@``-import of the framework's own contract (``docs/framework/contract.md``), which an upgrade
replaces whole and lint G-D0 compares with the installed kit. The ``SessionStart`` hook that runs
``orient`` goes into ``.claude/settings.local.json``, created only when absent: its command names
this machine's engine interpreter and repo root, so it is machine-local, like the MCP
registration.

Deliberately not here: installing anything (the engine runs from its own environment and is
never installed into the target repo's), registering the MCP server (a ``claude mcp add`` the
session runs, FRAMEWORK §8.0.2), merging the hook into a settings file that already exists, and
committing. ``init`` needs no ``context.toml``, because it
is what writes the first one.
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

from . import config as C
from .errors import Refusal

KIT = Path(__file__).with_name("kit")
TEMPLATE = "context.toml.template"
CONTRACT = "contract.md"  # the framework's rules; init copies it to CONTRACT_DEST and never edits it
CONTRACT_DEST = "docs/framework/contract.md"  # where kit/bootloader.md's import points
BOOTLOADER = "bootloader.md"  # what CLAUDE.md gets: the kit markers, the pin, the import
CONTRACT_TARGET = "CLAUDE.md"
SETTINGS = ".claude/settings.local.json"  # the SessionStart hook: machine-local (absolute paths)
SETTINGS_IGNORE = ".claude/.gitignore"
IMPORT_RE = re.compile(r"^@(\S+)[ \t]*$", re.MULTILINE)  # a CLAUDE.md import: `@path` on a line of its own
BEGIN, END = "<!-- context-engine kit 0.5 begin -->", "<!-- context-engine kit 0.5 end -->"
# any kit version's begin marker: an older block is the one an upgrade replaces, never a second one
ANY_BEGIN = re.compile(r"<!-- context-engine kit (\S+) begin -->")
# kit file -> where it goes in the repo
FILES = {
    "HANDOFF.md": "HANDOFF.md",
    "docs/charter.md": "docs/charter.md",
    "docs/criteria.md": "docs/criteria.md",
    "docs/ledger/session-log.md": "docs/ledger/session-log.md",
    # the by-hand fallback (P16): every operation, and every ritual in order; the repo's own copy
    "docs/runbooks/manual-mode.md": "docs/runbooks/manual-mode.md",
    "docs/runbooks/rituals.md": "docs/runbooks/rituals.md",
}
KEEP = ("docs/decisions", "docs/stories", "docs/working", "docs/evidence", "tasks")  # empty dirs get a .gitkeep
SELF_IGNORING = (".context", ".scratch")  # each holds a .gitignore of `*`
PREFIX_RE = re.compile(r"^[A-Z][A-Z0-9]*$")


def kit_block(text: str) -> tuple[str, str | None] | None:
    """The first kit block in ``text``, line endings normalised: (its version, the text between its
    begin and end markers, or None when no end marker follows). None when it holds no kit block."""
    norm = text.replace("\r\n", "\n")
    m = ANY_BEGIN.search(norm)
    if not m:
        return None
    j = norm.find(f"<!-- context-engine kit {m.group(1)} end -->", m.end())
    return m.group(1), (norm[m.end() : j] if j >= 0 else None)


def bootloader_body() -> str:
    """The text the kit's bootloader holds between its markers: what G-D0 expects there."""
    block = kit_block((KIT / BOOTLOADER).read_text(encoding="utf-8"))
    assert block and block[1] is not None, "kit/bootloader.md has no complete kit block"
    return block[1]


def hook_settings(root: Path) -> str:
    """``.claude/settings.local.json`` holding one ``SessionStart`` hook that runs ``orient`` on
    every source (startup, resume, clear, compact). The interpreter is the one running init, which
    is the engine's own; both paths are absolute and quoted, so the command needs no PATH entry, no
    environment variable. It runs under bash and cmd.exe (tested), not PowerShell (a quoted program
    needs `&` there); which shell Claude Code runs hooks in on Windows is not documented
    (docs/evidence/claude-code-hooks-2026-10-13.md), so that is a probe owed on a live session."""
    command = f'"{Path(sys.executable).as_posix()}" -m context_engine --root "{Path(root).resolve().as_posix()}" orient'
    return json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": command}]}]}}, indent=2) + "\n"


def has_hook(settings: Path) -> bool:
    """Whether a settings file already holds a SessionStart command that runs the engine's orient,
    so a re-run of init does not ask for a hook that is there. A file that is not JSON has none."""
    try:
        doc = json.loads(settings.read_bytes().decode("utf-8-sig"))
        entries = doc["hooks"]["SessionStart"]
        commands = [h.get("command", "") for e in entries for h in e.get("hooks", [])]
    except (ValueError, KeyError, TypeError, AttributeError):
        return False
    return any("-m context_engine" in c and c.rstrip().endswith("orient") for c in commands if isinstance(c, str))


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


def plan(root: Path, prefixes: dict[str, str] | None = None) -> tuple[dict[str, str], list[str], list[str], dict[str, str]]:
    """(path -> text to write, created, skipped, seen). ``CLAUDE.md``'s text is the whole new
    file, and ``seen`` holds the text it was planned from; every other write is a new file.

    A ``context.toml`` already present is kept, once it loads, and a skeleton or directory is then
    written only where that config points: a repo that mapped a component elsewhere (§11.4) does
    not get the kit's default file back on a re-run."""
    root = Path(root)
    writes: dict[str, str] = {}
    skipped: list[str] = []
    seen: dict[str, str] = {}
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
    block = (KIT / BOOTLOADER).read_text(encoding="utf-8")
    claude = root / CONTRACT_TARGET
    if not claude.exists():
        writes[CONTRACT_TARGET] = f"# {root.resolve().name}: contract\n\n" + block
    else:
        old = claude.read_bytes().decode("utf-8")
        have = ANY_BEGIN.search(old)
        if have and have.group(0) == BEGIN:
            found = kit_block(old)
            if found and found[1] is not None and IMPORT_RE.search(found[1]):
                skipped.append(CONTRACT_TARGET)
            else:  # the inline block from before the bootloader: its gate line may be filled in, so never by init
                skipped.append(f"{CONTRACT_TARGET} (holds the inline kit {have.group(1)} block: replace it with kit/{BOOTLOADER} by hand, kit README § Upgrade)")
        elif have:  # never a second block beside an older one: the upgrade replaces it (kit README § Upgrade)
            skipped.append(f"{CONTRACT_TARGET} (holds the kit {have.group(1)} block: replace it with kit/{BOOTLOADER} by hand, kit README § Upgrade)")
        else:
            norm = old.replace("\r\n", "\n")
            sep = "" if not norm or norm.endswith("\n\n") else ("\n" if norm.endswith("\n") else "\n\n")
            add = sep + block
            writes[CONTRACT_TARGET] = old + (add.replace("\n", "\r\n") if "\r\n" in old else add)
            seen[CONTRACT_TARGET] = old
    # the framework's own files, wherever the config maps the rest: the bootloader imports the
    # contract by this path, and the hook is what runs orient
    if (root / CONTRACT_DEST).exists():
        skipped.append(CONTRACT_DEST)
    else:
        writes[CONTRACT_DEST] = (KIT / CONTRACT).read_text(encoding="utf-8")
    if (root / SETTINGS).exists():  # it may hold the owner's permission grants: never merged into
        skipped.append(SETTINGS if has_hook(root / SETTINGS) else f"{SETTINGS} (add the SessionStart hook to it by hand: kit README § Hook)")
    else:
        writes[SETTINGS] = hook_settings(root)
        ignore = root / SETTINGS_IGNORE
        if not ignore.exists():
            writes[SETTINGS_IGNORE] = "settings.local.json\n"
        elif "settings.local.json" not in ignore.read_bytes().decode("utf-8", "replace").split():
            skipped.append(f"{SETTINGS_IGNORE} (it does not ignore settings.local.json, which holds this machine's paths: add that line)")
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
    return writes, list(writes), skipped, seen


def _write(root: Path, rel: str, text: str, seen: dict[str, str], done: list[str]) -> None:
    """Create ``rel``, refusing if it appeared after the plan; or, for the one file the plan read
    (``CLAUDE.md``), rewrite it only if it still holds the text the plan read."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    so_far = f"created so far: {', '.join(done) or 'none'}; run init again, it skips what exists"
    if rel in seen:
        now = path.read_bytes().decode("utf-8") if path.exists() else None
        if now != seen[rel]:
            raise Refusal(f"{rel} changed while init ran, so the bootloader was not appended", so_far)
        mode = "w"
    else:
        mode = "x"  # create only: a file that appeared after the plan is refused, never overwritten
    try:
        with open(path, mode, encoding="utf-8", newline="") as f:
            f.write(text)
    except FileExistsError:
        raise Refusal(f"{rel} appeared while init ran, so it was left as it is", so_far) from None
    done.append(rel)


def init(root: Path | str, prefixes: dict[str, str] | None = None, dry_run: bool = False) -> str:
    """Write what the repo is missing; return one line naming what was created and skipped."""
    root = Path(root)
    if not root.is_dir():
        raise Refusal(f"{root} is not a directory", "pass the repo root with --root")
    writes, created, skipped, seen = plan(root, prefixes)
    if not dry_run:
        done: list[str] = []
        for rel, text in writes.items():
            _write(root, rel, text, seen, done)
    verb = "would create" if dry_run else "created"
    head = "init (dry run)" if dry_run else "init"
    nxt = "" if dry_run or not created else "; next: fill docs/charter.md with the owner, register the MCP server, run lint"
    return f"{head}: {verb} {len(created)} ({', '.join(created) or 'none'}); skipped {len(skipped)} ({', '.join(skipped) or 'none'}){nxt}"
