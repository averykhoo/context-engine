"""``init``: write the adoption kit into a repo (FRAMEWORK §6.9, §11.4).

The kit is text in ``kit/`` beside this module, shipped as package data, so a plain
``pip install`` of the engine carries it and anyone can read it in the engine repo. ``init``
copies the files a repo is missing and creates the empty record directories. It only ever
creates: an existing file is never touched, except that ``CLAUDE.md`` gets the kit block
appended when no kit block (of any version) is in it yet, and the repo's ``.gitignore`` gets the
engine env's line appended when it does not ignore that yet (DEC-41). An existing ``context.toml`` is kept,
so init can be re-run after it is edited to fill in what is still missing.

The kit block (CE-38, US-17) is a few lines between the kit markers: the ``framework:`` pin and
an ``@``-import of the framework's own contract (``docs/framework/contract.md``), which an upgrade
replaces whole and lint G-D0 compares with the installed kit. The ``SessionStart`` hook that runs
``orient`` goes into ``.claude/settings.local.json``: its command names this machine's engine
interpreter and repo root, so it is machine-local, like the MCP registration. init creates that
file when absent; one that exists holds the owner's permission grants, so the hook goes into it
only with the owner's yes (``--merge-settings``, DEC-32), and nothing else in it changes.
``--skip-settings`` writes no hook at all, so a repo whose hook comes from the Claude Code plugin
(``plugin/`` in the engine repo, CE-77) gets no second one.

Deliberately not here: installing anything (the engine runs from its own pinned environment in
``.context-engine/env/``, made before init can run, and is never installed into the target repo's
own environment), registering the MCP server (a ``claude mcp add`` the
session runs, FRAMEWORK §8.0.2), and committing. ``init`` needs no ``context.toml``, because it
is what writes the first one.
"""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
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
GATE_PLACEHOLDER = "<this repo's own test command>"  # the bootloader's Gate stub, until the owner fills it in
SETTINGS = ".claude/settings.local.json"  # the SessionStart hook: machine-local (absolute paths)
SETTINGS_IGNORE = ".claude/.gitignore"
# DEC-41: a target repo's engine runs from a pinned, non-editable install in ENGINE_ENV, inside the
# repo's folder and gitignored, never from the repo's own env (kit README § 1). init cannot create
# it (it runs from it); it makes the repo's own .gitignore ignore ENGINE_DIR, so no clone commits it.
ENGINE_DIR = ".context-engine"
ENGINE_ENV = f"{ENGINE_DIR}/env"
REPO_IGNORE = ".gitignore"
ENGINE_IGNORE = f"# context-engine: the engine's pinned env (kit README § 1)\n{ENGINE_DIR}/\n"
APPENDED = (CONTRACT_TARGET, REPO_IGNORE)  # files init appends to in place, never replaces
# what --skip-settings says when there is no settings file: init writes no hook (CE-77)
SKIP_ABSENT = "--skip-settings: no hook written; the Claude Code plugin's hook runs orient, or add it by hand, kit README § Hook"
IMPORT_RE = re.compile(r"^@(\S+)[ \t]*$", re.MULTILINE)  # a CLAUDE.md import: `@path` on a line of its own
# the repo's own Gate heading (CE-51): level 1 or 2, the word Gate, then nothing or `(...`, `: ...`, ` - ...`
GATE_RE = re.compile(r"^ {0,3}#{1,2}[ \t]+Gate(?:[ \t]*[(:\u2013\u2014].*|[ \t]+-.*)?[ \t]*$", re.MULTILINE | re.IGNORECASE)
NEXT_HEADING_RE = re.compile(r"^ {0,3}#{1,2}[ \t]", re.MULTILINE)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[`~]*[ \t]*$", re.MULTILINE | re.DOTALL)  # a closed code fence
OPEN_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})", re.MULTILINE)  # left after FENCE_RE: a fence never closed
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
LINT_RE = re.compile(r"context[-_]engine\s+lint")  # a gate running lint: `context-engine lint` or `-m context_engine lint`
BEGIN, END = "<!-- context-engine kit 0.5 begin -->", "<!-- context-engine kit 0.5 end -->"
# any kit version's begin marker: an older block is the one an upgrade replaces, never a second one
ANY_BEGIN = re.compile(r"<!-- context-engine kit (\S+) begin -->")
# kit file -> where it goes in the repo
FILES = {
    "HANDOFF.md": "HANDOFF.md",
    "docs/charter.md": "docs/charter.md",
    "docs/criteria.md": "docs/criteria.md",
    "docs/ledger/session-log.md": "docs/ledger/session-log.md",
    # the by-hand fallback (P16): every operation, and every procedure's steps in order; the repo's own copy
    "docs/runbooks/manual-mode.md": "docs/runbooks/manual-mode.md",
    "docs/runbooks/procedures.md": "docs/runbooks/procedures.md",
    # the method runbooks (FRAMEWORK §7.5): framework-generic; the repo's values stay in its CLAUDE.md
    "docs/runbooks/gate.md": "docs/runbooks/gate.md",
    "docs/runbooks/sabotage.md": "docs/runbooks/sabotage.md",
    "docs/runbooks/fan-out.md": "docs/runbooks/fan-out.md",
    "docs/runbooks/release.md": "docs/runbooks/release.md",
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
    """The text the kit block (`kit/bootloader.md`) holds between its markers: what G-D0 expects there."""
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


def _hook_state(doc: object, want: str) -> tuple[str, str]:
    """``("ours", "")`` when the settings hold this repo's orient hook exactly: an entry with no
    matcher running the very command init writes for this machine and root (whitespace aside);
    ``("stale", <command>)`` when they hold another command running the engine's orient (a moved
    repo, a rebuilt interpreter), which init must not take for the hook; else ``("none", "")``."""
    stale = ""
    try:
        for entry in doc["hooks"]["SessionStart"]:  # type: ignore[index]
            for h in entry.get("hooks", []):
                c = h.get("command", "")
                if not isinstance(c, str):
                    continue
                if c.split() == want.split() and entry.get("matcher", "") in ("", "*"):
                    return "ours", ""
                if "context_engine" in c and "orient" in c:
                    stale = stale or c
    except (KeyError, TypeError, AttributeError):
        pass
    return ("stale", stale) if stale else ("none", "")


def _not_json(name: str) -> object:
    raise ValueError(f"{name} is not JSON")


def _finite(token: str) -> float:
    value = float(token)
    if math.isinf(value):
        raise ValueError(f"{token} overflows a float, so it could not be written back as JSON")
    return value


def _strict_json(text: str) -> object:
    """``json.loads``, refusing what a rewrite would change or lose: a key that appears twice (plain
    ``loads`` keeps the last one and the rewrite drops the other; the owner's grants live in this
    file), ``NaN`` and ``Infinity`` (not JSON), and a number that overflows a float."""

    def pairs(items: list[tuple[str, object]]) -> dict:
        keys = [k for k, _ in items]
        dup = sorted({k for k in keys if keys.count(k) > 1})
        if dup:
            raise ValueError(f"the key {dup[0]!r} appears twice")
        return dict(items)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=_not_json, parse_float=_finite)


def merged_settings(root: Path, old: str) -> str | None:
    """``old`` (the settings file's text) with the orient hook appended to ``hooks.SessionStart``,
    every other key and its order kept, the line endings and any BOM kept; None when it already
    holds the hook. Refuses text it cannot merge into without guessing: not strict JSON, or a
    ``hooks`` that is not an object or a ``SessionStart`` that is not a list (DEC-32)."""
    remedy = f"fix {SETTINGS} and run init again, or run it with --skip-settings and add the hook by hand (kit README § Hook)"
    try:
        doc = _strict_json(old.removeprefix("\ufeff"))
    except ValueError as e:
        raise Refusal(f"{SETTINGS} is not JSON init can merge into ({e}), so it was left untouched", remedy) from None
    if isinstance(doc, dict) and doc.get("disableAllHooks") is True:
        raise Refusal(f"{SETTINGS} sets disableAllHooks, so no hook would run, and it was left untouched", "the owner turned hooks off: run init with --skip-settings, and run orient by hand at session start")
    want = hook_entry(root)["hooks"][0]["command"]
    state, other = _hook_state(doc, want)
    if state == "ours":
        return None
    if state == "stale":
        raise Refusal(f"{SETTINGS} holds a SessionStart hook running the engine's orient with another command ({other}), so it was left untouched", f"have the owner replace that command with the one for this machine and this repo: {want}; or run init with --skip-settings")
    hooks = doc.get("hooks", {}) if isinstance(doc, dict) else None
    starts = hooks.get("SessionStart", []) if isinstance(hooks, dict) else None
    if not isinstance(starts, list):
        raise Refusal(f"{SETTINGS} is not shaped as init expects (an object at the top level, an object at `hooks`, a list at `hooks.SessionStart`), so it was left untouched", remedy)
    doc.setdefault("hooks", hooks)
    hooks["SessionStart"] = starts + [hook_entry(root)]
    text = json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as e:  # a lone surrogate escape parses, but has no UTF-8 form
        raise Refusal(f"{SETTINGS} holds a string with a lone surrogate escape ({e.reason}), which cannot be written back as UTF-8, so it was left untouched", remedy) from None
    return ("\ufeff" if old.startswith("\ufeff") else "") + (text.replace("\n", "\r\n") if "\r\n" in old else text)


def hook_entry(root: Path) -> dict:
    """The one ``SessionStart`` entry init adds: no matcher, one command hook running orient."""
    return json.loads(hook_settings(root))["hooks"]["SessionStart"][0]


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


def plan(root: Path, prefixes: dict[str, str] | None = None, settings: str = "") -> tuple[dict[str, str], list[str], list[str], dict[str, str], list[str]]:
    """(path -> text to write, created, skipped, seen, warnings). ``CLAUDE.md``'s text, and a
    settings file's the hook is merged into, are the whole new file, and ``seen`` holds the text
    each was planned from; every other write is a new file. ``settings`` is ``merge`` or ``skip``
    for a settings file that exists without the hook; with neither, that refuses, showing the
    change (DEC-32); ``preview`` (a dry run) names that question as a warning instead, so the
    owner sees the whole plan before answering it. ``warnings`` are what the owner must act on.

    A ``context.toml`` already present is kept, once it loads, and a skeleton or directory is then
    written only where that config points: a repo that mapped a component elsewhere (§11.4) does
    not get the kit's default file back on a re-run."""
    root = Path(root)
    writes: dict[str, str] = {}
    skipped: list[str] = []
    seen: dict[str, str] = {}
    warnings: list[str] = []
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
    labels: dict[str, str] = {}
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
            else:  # a block from before `kit/bootloader.md` that inlines the rules: its gate line may be filled in, so never by init
                skipped.append(f"{CONTRACT_TARGET} (holds a kit {have.group(1)} block that inlines the rules: replace it with kit/{BOOTLOADER} by hand, kit README § Upgrade)")
        elif have:  # never a second block beside an older one: the upgrade replaces it (kit README § Upgrade)
            skipped.append(f"{CONTRACT_TARGET} (holds the kit {have.group(1)} block: replace it with kit/{BOOTLOADER} by hand, kit README § Upgrade)")
        else:
            norm = old.replace("\r\n", "\n")
            sep = "" if not norm or norm.endswith("\n\n") else ("\n" if norm.endswith("\n") else "\n\n")
            gate = gate_section(norm)
            if gate:  # the repo's own gate stays the one gate: the kit block goes in without the stub (CE-51)
                block = block[: block.index(END) + len(END)] + "\n"
                lint = "" if LINT_RE.search(gate[1]) else ": make it end with `&& context-engine lint`"
                labels[CONTRACT_TARGET] = f'{CONTRACT_TARGET} (kit block appended without the Gate stub: it has its own "{gate[0]}"{lint})'
            add = sep + block
            writes[CONTRACT_TARGET] = old + (add.replace("\n", "\r\n") if "\r\n" in old else add)
            seen[CONTRACT_TARGET] = old
    # the framework's own files, wherever the config maps the rest: the kit block imports the
    # contract by this path, and the hook is what runs orient
    if (root / CONTRACT_DEST).exists():
        skipped.append(CONTRACT_DEST)
    else:
        writes[CONTRACT_DEST] = (KIT / CONTRACT).read_text(encoding="utf-8")
    if (root / SETTINGS).exists():  # it holds the owner's permission grants: changed only with their yes (DEC-32)
        if settings == "skip":
            label, ours = _skip_label(root)
            skipped.append(f"{SETTINGS} ({label})")
            if ours:
                _ensure_ignore(root, writes, skipped, warnings, write=False)
        else:
            old = _read_text(root / SETTINGS)
            new = merged_settings(root, old)
            if new is None:
                skipped.append(f"{SETTINGS} (holds the orient hook)")
                _ensure_ignore(root, writes, skipped, warnings, write=False)  # every run, not only the merging one (CE-70)
            elif settings == "preview":  # a dry run shows the question with the plan, never refuses on it
                skipped.append(f"{SETTINGS} (exists without the orient hook)")
                warnings.append(f"{SETTINGS} is the owner's call: init would append {json.dumps(hook_entry(root))} to hooks.SessionStart and change nothing else{_ignore_too(root)}; with a yes, run init with --merge-settings, with a no, with --skip-settings")
            elif settings != "merge":
                raise Refusal(
                    f"{SETTINGS} exists, so the hook goes into it: init would append {json.dumps(hook_entry(root))} to hooks.SessionStart and change nothing else{_ignore_too(root)}",
                    "show the owner that change and ask: with a yes, run init again with --merge-settings; with a no, with --skip-settings (the hook can be added by hand later, kit README § Hook)",
                )
            else:
                _replaceable(root / SETTINGS)
                writes[SETTINGS] = new
                seen[SETTINGS] = old
                labels[SETTINGS] = f"{SETTINGS} (the orient hook merged in)"
                _ensure_ignore(root, writes, skipped, warnings, write=True)
    elif settings == "skip":  # no hook from init: the plugin's runs orient, or the owner adds one by hand (CE-77)
        skipped.append(f"{SETTINGS} ({SKIP_ABSENT})")
    else:
        writes[SETTINGS] = hook_settings(root)
        _ensure_ignore(root, writes, skipped, warnings, write=True)
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
    _plan_engine_ignore(root, writes, skipped, seen, labels, warnings)
    return writes, [labels.get(k, k) for k in writes], skipped, seen, warnings


def _plan_engine_ignore(root: Path, writes: dict[str, str], skipped: list[str], seen: dict[str, str], labels: dict[str, str], warnings: list[str]) -> None:
    """The repo's own ``.gitignore`` ignores ``ENGINE_DIR`` (DEC-41): created holding the line when
    absent, the line appended (in the file's line endings) when it does not ignore it yet, and left
    alone when it does. A tracked root line, not a self-ignoring ``.gitignore`` in the directory,
    because every clone rebuilds the env there and must not see it as untracked."""
    path = root / REPO_IGNORE
    if not path.exists():
        writes[REPO_IGNORE] = ENGINE_IGNORE
        return
    try:
        old = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        skipped.append(REPO_IGNORE)
        warnings.append(f"{REPO_IGNORE} is not UTF-8, so init left it alone: add the line {ENGINE_DIR}/ to it, which the engine's env needs (kit README § 1)")
        return
    if _engine_ignored(old):
        skipped.append(f"{REPO_IGNORE} (ignores {ENGINE_DIR}/)")
        return
    norm = old.replace("\r\n", "\n")
    sep = "" if not norm or norm.endswith("\n\n") else ("\n" if norm.endswith("\n") else "\n\n")
    add = sep + ENGINE_IGNORE
    writes[REPO_IGNORE] = old + (add.replace("\n", "\r\n") if "\r\n" in old else add)
    seen[REPO_IGNORE] = old
    labels[REPO_IGNORE] = f"{REPO_IGNORE} ({ENGINE_DIR}/ appended)"


def _engine_ignored(text: str) -> bool:
    """Whether a root ``.gitignore`` holding ``text`` ignores ``ENGINE_DIR``, the last matching line
    winning as in git (a `!` line re-includes). An approximation of ``git check-ignore`` that errs
    only toward appending the line, which is harmless (the appended line comes last, so a re-run
    finds it): a line naming only something inside the directory (`.context-engine/env/`) does not
    count, a leading space stays part of the pattern as in git, and a later `!` line that may
    re-include anything inside it (`!.context-engine/env/`, or an unanchored `!env/`) undoes it."""
    import fnmatch

    state = False
    for ln in text.splitlines():
        ln = ln.rstrip()  # git drops trailing spaces but keeps leading ones
        if not ln or ln.startswith("#"):
            continue
        neg = ln.startswith("!")
        raw = (ln[1:] if neg else ln).rstrip("/")
        pat = raw.lstrip("/")
        top = pat.split("/")[0]
        if pat in (f"{ENGINE_DIR}/*", f"{ENGINE_DIR}/**") or fnmatch.fnmatchcase(ENGINE_DIR, pat):
            state = not neg
        elif neg and ("/" not in raw or fnmatch.fnmatchcase(ENGINE_DIR, top)):  # a `*` or `**` top matches too
            state = False  # unanchored, or anchored inside ENGINE_DIR: it may re-include part of the env
    return state


def gate_section(text: str) -> tuple[str, str] | None:
    """The Gate section of ``text`` (a ``CLAUDE.md``): its heading and its text up to the next
    heading of level 1 or 2; None when it has none. Only a level 1 or 2 heading reading `Gate`
    (optionally followed by a parenthesis, a colon or a dash and more words) counts, outside code
    fences and HTML comments: the repo's own gate, which the kit block's stub must not double
    (CE-51). A `### Gate` under another section, or `## Gate-keeping`, is not the repo's gate."""
    prose = FENCE_RE.sub("", text.replace("\r\n", "\n").removeprefix("\ufeff"))
    prose = prose[: m.start()] if (m := OPEN_FENCE_RE.search(prose)) else prose  # an unclosed fence runs to the end
    prose = COMMENT_RE.sub("", prose)
    m = GATE_RE.search(prose)
    if not m:
        return None
    nxt = NEXT_HEADING_RE.search(prose, m.end())
    return m.group(0).strip(), prose[m.end() : nxt.start() if nxt else len(prose)]


def _skip_label(root: Path) -> tuple[str, bool]:
    """What ``--skip-settings`` says of a settings file it leaves alone, and whether that file holds
    this repo's orient hook. Read leniently: under ``--skip-settings`` a file init cannot read or
    parse is the owner's to fix, never a refusal (CE-70)."""
    by_hand = "--skip-settings: add the SessionStart hook by hand, kit README § Hook"
    try:
        doc = _strict_json(_read_text(root / SETTINGS).removeprefix("\ufeff"))
    except (Refusal, ValueError, OSError):
        return by_hand, False
    if isinstance(doc, dict) and doc.get("disableAllHooks") is True:
        return "--skip-settings: it sets disableAllHooks, so no hook runs: run orient by hand at session start", False
    want = hook_entry(root)["hooks"][0]["command"]
    state, other = _hook_state(doc, want)
    if state == "ours":
        return "holds the orient hook", True
    if state == "stale":
        return f"--skip-settings: its orient hook runs another command ({other}): have the owner replace it with {want}", False
    return by_hand, False


def _ensure_ignore(root: Path, writes: dict[str, str], skipped: list[str], warnings: list[str], *, write: bool) -> None:
    """The settings file holds (or is about to hold) the hook, with this machine's paths, so git
    must ignore it. When init writes the hook (``write``), it also writes a missing
    ``.claude/.gitignore``; otherwise, and when one exists without the line, it names the gap, on
    every run that finds the hook, so a re-run repeats the warning until it is fixed (CE-70)."""
    if _ignored(root):
        return
    if not (root / SETTINGS_IGNORE).exists():
        if write:
            writes[SETTINGS_IGNORE] = "settings.local.json\n"
        else:
            warnings.append(f"{SETTINGS_IGNORE} is absent and nothing init reads ignores settings.local.json, which holds this machine's paths: create it holding that line, or ignore the file in the repo's own .gitignore")
    else:
        skipped.append(SETTINGS_IGNORE)
        warnings.append(f"{SETTINGS_IGNORE} (it does not ignore settings.local.json, which holds this machine's paths: add that line, or check the repo's own .gitignore does)")


def _ignore_too(root: Path) -> str:
    """What else the owner's yes to the merge brings (DEC-32 asks for it knowing all of it): the
    ``.claude/.gitignore`` that ``_ensure_ignore`` then writes, when nothing ignores the file."""
    if _ignored(root) or (root / SETTINGS_IGNORE).exists():
        return ""
    return f" in it, and would write {SETTINGS_IGNORE} holding settings.local.json beside it (nothing ignores that file)"


def _ignore_lines(path: Path) -> list[str]:
    try:
        text = path.read_bytes().decode("utf-8", "replace") if path.is_file() else ""
    except OSError:
        return []
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def _ignored(root: Path) -> bool:
    """Whether the repo's own ``.gitignore`` and then ``.claude/.gitignore`` ignore the settings
    file, read the way git reads them: the last matching line wins, a negation (`!`) re-includes,
    a deeper file overrides the root one, and an excluded ``.claude`` directory cannot be
    re-included. An approximation of ``git check-ignore`` (init does not use git): it does not read
    ``.git/info/exclude``, ``core.excludesFile`` or other nested files, so it errs toward writing
    the ignore file, or a warning (CE-70)."""
    import fnmatch

    state = False
    for ln in _ignore_lines(root / ".gitignore"):
        neg = ln.startswith("!")
        pat = (ln[1:] if neg else ln).lstrip("/")
        if pat.rstrip("/") == ".claude":  # the directory itself: nothing under it can be re-included
            if not neg:
                return True
            continue
        if fnmatch.fnmatchcase(".claude/settings.local.json", pat) or ("/" not in pat and fnmatch.fnmatchcase("settings.local.json", pat)):
            state = not neg
    for ln in _ignore_lines(root / SETTINGS_IGNORE):
        neg = ln.startswith("!")
        if fnmatch.fnmatchcase("settings.local.json", (ln[1:] if neg else ln).lstrip("/")):
            state = not neg
    return state


def _replaceable(path: Path) -> None:
    """Refuse, at plan time and so before any write, a settings file the merge cannot replace
    whole without harm: hard-linked (the replace would split the link) or not writable."""
    target = Path(os.path.realpath(path))  # a symlink is followed: the file it names is replaced
    remedy = "add the hook by hand (kit README § Hook), or run init with --skip-settings"
    if target.stat().st_nlink > 1:
        raise Refusal(f"{SETTINGS} is hard-linked, and replacing it would split the link, so it was left untouched", remedy)
    if not os.access(target, os.W_OK):
        raise Refusal(f"{SETTINGS} is not writable, so it was left untouched", "make it writable and run init again, or " + remedy)


def _read_text(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as e:
        raise Refusal(f"{path.name} is not UTF-8 ({e.reason} at byte {e.start}), so it was left untouched", "save it as UTF-8, then run init again") from None


def _current(path: Path) -> str | None:
    return path.read_bytes().decode("utf-8", "replace") if path.exists() else None


def _write(root: Path, rel: str, text: str, seen: dict[str, str], done: list[str]) -> None:
    """Create ``rel``, refusing if it appeared after the plan; or, for a file the plan read, write
    it only if it still holds the text the plan read. ``CLAUDE.md`` is written in place, so a
    linked one stays linked. A settings file the hook is merged into is written to a temp file,
    re-read, and replaced whole, atomically: Claude Code writes the owner's permission grants into
    it, and a grant written before the re-read is kept by refusing. One written in the instant
    between the re-read and the replace is lost: there is no lock shared with Claude Code."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    so_far = f"created so far: {', '.join(done) or 'none'}; run init again, it skips what exists"
    if rel in APPENDED and rel in seen:
        if _current(path) != seen[rel]:
            what = "the kit block" if rel == CONTRACT_TARGET else f"{ENGINE_DIR}/"
            raise Refusal(f"{rel} changed while init ran, so {what} was not appended", so_far)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        done.append(rel)
        return
    if rel in seen:
        target = Path(os.path.realpath(path))
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=f"{target.name}.", suffix=".init.tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            if _current(path) != seen[rel]:
                raise Refusal(f"{rel} changed while init ran, so nothing was written to it", so_far)
            try:
                os.replace(tmp, target)
            except OSError as e:
                raise Refusal(f"{rel} could not be replaced ({e.strerror or e}), so nothing was written to it", f"close whatever holds it open, then run init again; {so_far}") from None
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        done.append(rel)
        return
    mode = "x"  # create only: a file that appeared after the plan is refused, never overwritten
    try:
        with open(path, mode, encoding="utf-8", newline="") as f:
            f.write(text)
    except FileExistsError:
        raise Refusal(f"{rel} appeared while init ran, so it was left as it is", so_far) from None
    done.append(rel)


def next_steps(claude: str) -> str:
    """The bootstrap steps after init, in the kit README's order (§ 2a). The gate step replaces the
    stub's placeholder while ``claude`` (CLAUDE.md as init left it) holds it, and otherwise asks for
    a check of the gate the repo had; the MCP server is optional, so it is named as such, not as a
    step (CE-70)."""
    if GATE_PLACEHOLDER in claude:
        gate = f"replace `{GATE_PLACEHOLDER}` in {CONTRACT_TARGET} § Gate with the repo's test command, "
    else:
        gate = f"check {CONTRACT_TARGET} § Gate runs the repo's tests and ends with `&& context-engine lint`, "
    return (
        f"fill docs/charter.md with the owner, {gate}run lint, commit the kit's files by path, then `session start`"
        " (registering the MCP server is optional: kit README § 1)"
    )


def init(root: Path | str, prefixes: dict[str, str] | None = None, dry_run: bool = False, merge_settings: bool = False, skip_settings: bool = False) -> str:
    """Write what the repo is missing; return one line naming what was created and skipped.
    ``merge_settings`` (the owner said yes) adds the hook to a settings file that exists;
    ``skip_settings`` (they said no) leaves it alone."""
    root = Path(root)
    if not root.is_dir():
        raise Refusal(f"{root} is not a directory", "pass the repo root with --root")
    if merge_settings and skip_settings:
        raise Refusal("--merge-settings and --skip-settings contradict each other", "pass the one the owner chose")
    writes, created, skipped, seen, warnings = plan(root, prefixes, "merge" if merge_settings else "skip" if skip_settings else "preview" if dry_run else "")
    if not dry_run:
        done: list[str] = []
        for rel, text in writes.items():
            _write(root, rel, text, seen, done)
    verb = "would create" if dry_run else "created"
    head = "init (dry run)" if dry_run else "init"
    bootstrap = C.CONFIG_NAME in writes or CONTRACT_TARGET in writes  # a re-run that only fills a gap is no bootstrap
    nxt = "" if dry_run or not bootstrap else "; next: " + next_steps(writes.get(CONTRACT_TARGET) or _current(root / CONTRACT_TARGET) or "")
    warn = "".join(f"; warning: {w}" for w in warnings)  # what the owner must act on, apart from what was skipped
    return f"{head}: {verb} {len(created)} ({', '.join(created) or 'none'}); skipped {len(skipped)} ({', '.join(skipped) or 'none'}){warn}{nxt}"
