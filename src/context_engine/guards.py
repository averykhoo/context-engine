"""The guard catalogue's doc, trace and tool-ownership guards (FRAMEWORK §8.2 to §8.4; CE-14).

Each guard is one function from an :class:`~context_engine.working.Engine` to a list of
:class:`~context_engine.store.Failure`, and each docstring says what it deliberately does not
check (P7). ``lint`` runs them all; ``Engine.lint`` drops the ids ``[guards] off`` names.

What a doc guard reads is configured, never guessed: G-D1's caps sit on ``[[routes]]``, and G-D3,
G-T3 and G-D7 read the paths listed in ``[guards]``. A path list that is empty checks nothing.
G-D12 reads the spec and the coverage maps ``[guards]`` names, and is off while neither is set.
G-T3 also reads the `code:` links of the ``[working] decision`` kind's current records. G-D4
reads ``[guards] liveness`` and ``history`` (with ``liveness_given`` for docs whose opening lines
the repo may not edit), and G-D5 reads ``[guards] numbers``; each is off while its lists are empty.

The correctness chain (G-I1, G-I2, G-T1, G-T2, G-T6; CE-25) reads ``[guards] charter``, ``stories``,
``tests`` and ``claim`` with ``[working] criteria``: a guard is off while a source it needs is unset,
and red when a set path is missing or a source yields nothing (no goal row, no criterion row, no
claim), so a reworded table or a pattern that does not fit cannot pass by finding nothing.

Not here (FRAMEWORK §8, with their homes): G-T5 mutation per criterion, G-T4 structural anchors, G-T7 deviations, G-W9 to G-W11 (housekeeping), G-V1 to
G-V3 (the run ledger).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import TYPE_CHECKING, Iterator

from . import decisions as D
from . import gate as GATE
from . import ledger as L
from .bootstrap import ENGINE_DIR
from .config import CONFIG_NAME, LIVENESS
from .errors import Refusal
from .store import ALIASES, Failure, key_order

if TYPE_CHECKING:
    from .working import Engine

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")  # a fence line: its marker run, then the info string (CE-61)
# a frontmatter line (CE-61): a `key:` line, a list item, an indented continuation, a comment, or blank
FM_KEY_RE = re.compile(r"^[A-Za-z_][\w.-]*\s*:(?:\s|$)")
FM_LINE_RE = re.compile(r"^(?:[A-Za-z_][\w.-]*\s*:(?:\s|$)|\s*-(?:\s|$)|\s+\S|\s*#|\s*$)")
SPAN_RE = re.compile(r"`([^`\n]+)`")
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*<?(\S+?)>?(?:\s|$)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# a `file::symbol` span: a path with a `/` or a file extension, then a dotted name (`()` allowed)
CODE_REF_RE = re.compile(r"^(?P<file>[\w.\-/]*(?:/|\.[A-Za-z0-9]+)[\w.\-/]*)::(?P<symbol>[A-Za-z_][\w.]*)(?:\(\))?$")
# a span naming a file: a path with a `/`, or a name with an extension the repo keeps text in
PATH_SPAN_RE = re.compile(r"^(?P<file>[\w][\w.\-/]*?\.(?:py|md|toml|json|jsonl|yml|yaml|txt|cfg|ini|sh|ps1|feature)|[\w][\w.\-]*(?:/[\w.\-]+)+/?)$")
HISTORY_MARK = "*HISTORY —*"
KEY_RE = r"\d{4}-\d{2}-\d{2}[a-z]+"
WARN = "⚠"
BOLD_CAPS_RE = re.compile(r"\*\*(?=[^*\n]*[A-Z]{4})[^*a-z\n]+\*\*")
STRING_RE = re.compile(r"\"(?:[^\"\\]|\\.)*\"|'[^']*'")  # TOML strings, blanked before a `#` is read as a comment
NUMBER_KEY_RE = re.compile(r"([\w-]+)\s*=\s*[-+]?\d[\d_]*(?:\.\d+)?(?=\s*(?:[,}\]]|$))")  # `key = 12`, also inside `{ ... }`
PROVENANCE_RE = re.compile(r"provenance:\s*(MEASURED|JUDGEMENT)\b")
SKIP_DIRS = {".git", ".scratch", ".context", ENGINE_DIR, "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache"}  # ENGINE_DIR holds the engine's env (kit README § 1)


def lint(e: Engine) -> list[Failure]:
    return caps(e) + ids(e) + links(e) + supersede_links(e) + liveness(e) + numbers(e) + signals(e) + note_layers(e) + provenance(e) + existence(e) + tool_owned(e) + op_records(e) + coverage(e) + intent(e)


# -- shared reading ----------------------------------------------------------------------


def _text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")


def _deprecated(text: str) -> bool:
    """An OKF record no longer current (`status: deprecated`): a closed task, a superseded decision."""
    m = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
    return bool(m and re.search(r"^status:\s*deprecated\s*$", m.group(1), re.MULTILINE))


def docs(root: Path, paths: tuple[str, ...]) -> Iterator[tuple[str, Path | None]]:
    """Each listed file, and each ``.md`` under a listed directory, as (repo-relative path, path).
    A listed path that does not exist comes back with ``None``."""
    for rel in paths:
        p = root / rel
        if p.is_file():
            yield rel, p
        elif p.is_dir():
            for f in sorted(p.rglob("*.md")):
                if not SKIP_DIRS.intersection(f.relative_to(root).parts):
                    yield f.relative_to(root).as_posix(), f
        else:
            yield rel, None


def frontmatter_end(lines: list[str]) -> int | None:
    """The index of the `---` that closes a frontmatter block opening ``lines``, or None when
    there is none (CE-61): the block opens on line one, closes on a later `---`, holds at least one
    `key:` line and nothing but YAML key lines, list items, indented continuations, comments and
    blank lines. A doc opening with a thematic break (`---`, then prose) has no frontmatter."""
    if not lines or lines[0] != "---":
        return None
    end = next((j for j in range(1, len(lines)) if lines[j] == "---"), None)
    if end is None:
        return None
    block = lines[1:end]
    if not any(FM_KEY_RE.match(ln) for ln in block) or not all(FM_LINE_RE.match(ln) for ln in block):
        return None
    return end


def prose(text: str, history: bool = False) -> Iterator[tuple[int, str]]:
    """(line number, line) outside fenced code and frontmatter, with inline code kept. With
    ``history``, blockquotes and lines carrying a ``*HISTORY —*`` note are skipped too.

    A fence closes only on a run of its own marker (backtick or tilde) at least as long as the one
    that opened it, with nothing after it (CommonMark), so a `~~~` inside a backtick fence is code
    (CE-61); frontmatter is read by ``frontmatter_end``. An unclosed fence runs to the end."""
    lines = text.split("\n")
    end = frontmatter_end(lines)
    i = 0 if end is None else end + 1
    fence: str | None = None  # the opening marker run while inside a fence
    for n in range(i, len(lines)):
        line = lines[n]
        m = FENCE_RE.match(line)
        if fence is None and m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            fence = m.group(1)
            continue
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
                fence = None
            continue
        if history and (line.lstrip().startswith(">") or HISTORY_MARK in line):
            continue
        yield n + 1, line


class Files:
    """The repo's files by name, read once per lint run, for case-exact lookups."""

    def __init__(self, root: Path):
        self.root = root
        self._by_name: dict[str, list[str]] | None = None

    def case_exact(self, rel: str, base: Path | None = None) -> Path | None:
        """``rel`` under ``base`` (the repo root by default) if every part exists with exactly that
        case. Case-insensitive file systems would otherwise find `Store.py` for `store.py`."""
        here = base or self.root
        for part in Path(rel).parts:
            if part == ".":
                continue
            if part == "..":
                here = here.parent
                continue
            if not here.is_dir() or part not in os.listdir(here):
                return None
            here = here / part
        return here

    def named(self, name: str) -> list[str]:
        """Every repo path whose file name is ``name``, less what git ignores (CE-41: a stale copy
        under `build/` is no answer). Outside a git work tree, a walk that skips `build/` and `dist/`."""
        if self._by_name is None:
            self._by_name = {}
            try:
                paths = [r for r in GATE.files(self.root) if not SKIP_DIRS.intersection(r.split("/"))]
            except Refusal:
                paths = []
                for d, dirs, files in os.walk(self.root):
                    dirs[:] = [x for x in dirs if x not in SKIP_DIRS | {"build", "dist"} and not x.endswith(".egg-info")]
                    paths += [(Path(d) / f).relative_to(self.root).as_posix() for f in files]
            for r in paths:
                self._by_name.setdefault(r.rsplit("/", 1)[-1], []).append(r)
        return self._by_name.get(name, [])

    def find(self, rel: str) -> Path | None:
        """A repo path, case-exact; a bare file name resolves to any file of that name."""
        rel = rel.rstrip("/")
        hit = self.case_exact(rel)
        if hit is None and "/" not in rel:
            names = self.named(rel)
            hit = self.root / names[0] if names else None
        return hit


def symbol_missing(path: Path, symbol: str) -> str | None:
    """The first dotted part of ``symbol`` the file does not name as a word, or None."""
    text = path.read_bytes().decode("utf-8", errors="replace") if path.is_file() else ""
    return next((p for p in symbol.split(".") if not re.search(rf"\b{re.escape(p)}\b", text)), None)


def code_ref_problem(files: Files, file: str, symbol: str) -> str | None:
    hit = files.find(file)
    if hit is None:
        return f"`{file}` does not exist (case-exact)"
    if symbol:
        missing = symbol_missing(hit, symbol)
        if missing:
            return f"`{file}` has no `{missing}` (from `{file}::{symbol}`)"
    return None


def code_link_problem(files: Files, link: str) -> tuple[str, str] | None:
    """Why a decision's `code:` link names no code, with its remedy, or None (CE-35). A link is
    `file` or `file::symbol`: a path from the repo root, written with `/`, that stays inside the
    repo and names a file (not a directory) existing case-exact, and a symbol whose every dotted
    part is non-empty and named in the file as a word. `decision link` and `decision relink`
    refuse what this names, and G-T3 fails a stored link it names, so a dead link cannot be
    replaced by one that names nothing."""
    file, sep, symbol = link.partition("::")
    if "\\" in file:
        return f"`{file}` is written with `\\`", "write the path with `/`: a `\\` path resolves on Windows only"
    parts = Path(file).parts
    if file.startswith("/") or re.match(r"[A-Za-z]:", file) or ".." in parts:
        return f"`{file}` is not a path inside the repo", "link a path from the repo root, with no `..` and no leading `/` or drive"
    if not parts:
        return f"`{link}` names no file", "link a repo file: `path/to/file.py` or `path/to/file.py::Name`"
    hit = files.case_exact(file)
    if hit is None:
        return f"`{file}` does not exist (case-exact)", "link a file that exists, with its exact case"
    if not hit.is_file():
        return f"`{file}` is a directory, not a file", "link a file in it, or a symbol in that file"
    if sep and not all(symbol.split(".")):
        return f"`{link}` has an empty symbol part", "name the symbol after `::`, dotted as `Class.method`, or drop the `::`"
    missing = symbol_missing(hit, symbol) if symbol else None
    if missing:
        return f"`{file}` has no `{missing}`", "grep for the symbol and link the name that exists"
    return None


def slug(heading: str) -> str:
    """GitHub's anchor for a heading: link text kept, lower case, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def anchors(text: str) -> set[str]:
    out: set[str] = set()
    for _, line in prose(text):
        m = HEADING_RE.match(line)
        if m:
            base = slug(m.group(2))
            a, n = base, 0
            while a in out:
                n += 1
                a = f"{base}-{n}"
            out.add(a)
    return out


# -- G-D1 caps ---------------------------------------------------------------------------


def caps(e: Engine) -> list[Failure]:
    """G-D1: every routed component under its caps (`max_lines`, `max_bytes`, `max_width` on its
    `[[routes]]` entry): the routed file, or each `.md` under a routed directory.

    Not checked: table rows against `max_width` (a table cannot wrap), files other than `.md`
    under a routed directory, and a route with no caps (it has none to break)."""
    out: list[Failure] = []
    for r in e.store.config.routes:
        if not (r.max_lines or r.max_bytes or r.max_width):
            continue
        for rel, path in docs(e.root, (r.path,)):
            if path is None:
                continue  # G-R1 reports a missing routed path
            out += cap_failures(r, rel, _text(path))
    return out


def cap_failures(r, rel: str, text: str) -> list[Failure]:
    """G-D1 on one doc's text, under route ``r``'s caps: lint's check, and a write's (CE-63)."""
    out: list[Failure] = []
    lines = text.split("\n")
    if text.endswith("\n"):
        lines = lines[:-1]
    remedy = f"move what has gone stale out (archive, the ledger, a decision or an evidence doc); raise the cap in [[routes]] {r.component!r} only with a new provenance note"
    if r.max_lines and len(lines) > r.max_lines:
        out.append(Failure("G-D1", rel, f"{len(lines)} lines, over the {r.component} cap of {r.max_lines}", remedy))
    size = len(text.encode("utf-8"))
    if r.max_bytes and size > r.max_bytes:
        out.append(Failure("G-D1", rel, f"{size} bytes, over the {r.component} cap of {r.max_bytes}", remedy))
    if r.max_width:
        wide = [(n, len(ln)) for n, ln in enumerate(lines, 1) if len(ln) > r.max_width and not ln.lstrip().startswith("|")]
        if wide:
            n, w = wide[0]
            out.append(Failure("G-D1", rel, f"{len(wide)} lines wider than {r.max_width} characters (the first: line {n}, {w})", "wrap them; tables are exempt"))
    return out


def _listed(rel: str, paths: tuple[str, ...]) -> bool:
    """``rel`` is one of ``paths``, or a ``.md`` under one that is a directory: what ``docs``
    yields for them, for a file not written yet."""
    for p in paths:
        p = p.rstrip("/")
        if rel == p or (rel.endswith(".md") and rel.startswith(p + "/") and not SKIP_DIRS.intersection(rel.split("/"))):
            return True
    return False


def prose_failures(e: Engine, rel: str, text: str) -> list[Failure]:
    """The guards lint runs on one prose doc, run on ``text`` (what a write is about to store at
    ``rel``) instead of the stored file (CE-63): G-D1 under each route that caps it, G-D5 when
    `[guards] numbers` lists it and it is neither FROZEN nor ACTIVE-PLAN, and G-D8 when it is the
    orientation note; less those `[guards] off` names. The same functions lint calls, so a write
    refuses only what lint would fail.

    Not checked: the doc-set failures (a listed path missing, a `numbers` list that checks
    nothing), and every other guard (lint, in the gate)."""
    out: list[Failure] = []
    for r in e.store.config.routes:
        if (r.max_lines or r.max_bytes or r.max_width) and _listed(rel, (r.path,)):
            out += cap_failures(r, rel, text)
    g = e.store.config.guards
    if g.numbers and _listed(rel, g.numbers) and liveness_of(e, rel, text, given(e)[0]) not in ("FROZEN", "ACTIVE-PLAN"):
        out += count_failures(rel, text, g.count_nouns)
    if e.w.handoff and rel == e.w.handoff:
        out += layer_failures(rel, text)
    off = set(g.off)
    return [f for f in out if f.guard not in off]


# -- G-D2 ids ----------------------------------------------------------------------------


def ids(e: Engine) -> list[Failure]:
    """G-D2 on the stored files: no two files of a series carry the same id (by file name or by `id:`),
    the op log never shows an id created twice (a reuse), and every alias (a record's earlier id,
    `aliases:`) resolves to one record: it is one word, not the record's own id, not in the form of
    a configured series, and carried by no other record (``Store.alias_problems``, which every
    write applies too).

    Not checked: an id reused before the op log began, or after a record was deleted outside the
    engine with no op logged (allocation already scans closed records and never reuses, AC-4); and
    whether an alias was ever really the record's id (it is provenance, set when the record is)."""
    out: list[Failure] = []
    st = e.store
    amap = st.alias_map()
    for kind in st.config.kinds.values():
        seen: dict[str, list[str]] = {}
        for path in st._files(kind):
            names = {st._id_of(kind, path)}
            try:
                head = st.read(path)
                fid = head.get("id")
            except Exception:
                head, fid = None, None  # the schema check reports an unreadable record
            if head is not None and head.get(ALIASES) and names != {None}:
                rid = st._id_of(kind, path)
                for msg, remedy in st.alias_problems(rid, head.get(ALIASES), amap):
                    out.append(Failure("G-D2", st._rel(path), msg, remedy))
            if fid and kind.id_re.match(str(fid)):
                names.add(str(fid))
            for rid in names - {None}:
                seen.setdefault(rid, []).append(st._rel(path))
        for rid, paths in sorted(seen.items()):
            if len(paths) > 1:
                out.append(Failure("G-D2", paths[0], f"id {rid} is carried by {len(paths)} files ({', '.join(paths)})", "give the newer record the next free id by hand (ids are never reused), then fix what cites it"))
    created: dict[str, str] = {}
    for n, op in _ops(e):
        if isinstance(op, dict) and op.get("op") in ("new", "import") and op.get("id"):
            rid = str(op["id"])
            if rid in created:
                out.append(Failure("G-D2", e.store.config.oplog, f"{rid} was created twice (sessions {created[rid]} and {op.get('session')}, op log line {n}): an id was reused", "renumber the newer record by hand to the next free id; ids are never reused"))
            created[rid] = str(op.get("session"))
    return out


def _ops(e: Engine) -> list[tuple[int, object]]:
    path = e.root / e.store.config.oplog
    if not path.is_file():
        return []
    out: list[tuple[int, object]] = []
    for n, line in enumerate(_text(path).split("\n"), 1):
        if line.strip():
            try:
                out.append((n, json.loads(line)))
            except ValueError:
                out.append((n, None))
    return out


# -- G-D3 links and `file::symbol` -------------------------------------------------------


def links(e: Engine) -> list[Failure]:
    """G-D3: in each doc `[guards] links` lists, every relative markdown link (and its `#anchor`)
    and every backticked `file::symbol` resolves, case-exact. A bare file name in a
    `file::symbol` resolves to any file of that name in the repo that git does not ignore (never a
    stale `build/` copy, CE-41); a symbol resolves when each of
    its dotted parts is a word in the file.

    Not checked: URLs (anything with a scheme), fenced code, an anchor into a file that is not
    markdown, which definition a symbol word is (a grep, not an import), and records no longer
    current (`status: deprecated`: a closed task or a superseded decision is history)."""
    out: list[Failure] = []
    files = Files(e.root)
    texts: dict[Path, set[str]] = {}

    def anchors_of(p: Path) -> set[str]:
        if p not in texts:
            texts[p] = anchors(_text(p))
        return texts[p]

    for rel, path in docs(e.root, e.store.config.guards.links):
        if path is None:
            out.append(Failure("G-D3", CONFIG_NAME, f"[guards] links names {rel}, which does not exist", "fix the path, or drop it from [guards] links"))
            continue
        text = _text(path)
        if _deprecated(text):
            continue
        bad: list[str] = []
        for n, line in prose(text):
            code = SPAN_RE.findall(line)
            for span in code:
                m = CODE_REF_RE.match(span.strip())
                if m:
                    p = code_ref_problem(files, m["file"], m["symbol"])
                    if p:
                        bad.append(f"line {n}: {p}")
            bare = SPAN_RE.sub("", line)
            targets = [m.group(1) for m in LINK_RE.finditer(bare)]
            rd = REF_DEF_RE.match(bare)
            if rd:
                targets.append(rd.group(1))
            for t in targets:
                if SCHEME_RE.match(t):
                    continue
                target, _, frag = t.partition("#")
                hit = files.case_exact(target, path.parent) if target else path
                if hit is None or not hit.exists():
                    bad.append(f"line {n}: link `{t}` points at nothing (case-exact)")
                elif frag and hit.is_file() and hit.suffix == ".md" and frag not in anchors_of(hit):
                    bad.append(f"line {n}: link `{t}` names no heading of {hit.name}")
        out += [Failure("G-D3", rel, b, "point it at the path, heading or symbol that exists (grep it first), or drop it") for b in bad]
    return out


MIRROR = {"supersedes": "superseded_by", "superseded_by": "supersedes"}


def supersede_links(e: Engine) -> list[Failure]:
    """G-D3 on the `supersedes` and `superseded_by` links of every record kind's records, stories
    and decisions alike (CE-57, INV-52): no record names itself; each id a link names resolves to a
    record of the same kind (directly or by an alias) and names this record back in the mirrored
    key; and the chain has no cycle. `record retire` and `decision supersede` write both sides, so
    a failure here is a hand edit, named with the record and the side that is missing.

    Not checked: a link naming no record of the story kind (G-I2 reports it, with its own remedy),
    whether the record that is superseded is also retired or `SUPERSEDED` (G-I2 for stories, the
    decision's own status), and links between kinds (no operation writes one)."""
    st = e.store
    amap = st.alias_map()
    stories = e.store.config.guards.stories
    out: list[Failure] = []
    for kind in st.config.kinds.values():
        heads: dict[str, tuple[str, object]] = {}
        for path in st._files(kind):
            rid = st._id_of(kind, path)
            if not rid:
                continue
            try:
                heads[rid] = (st._rel(path), st.read(path))
            except Exception:
                continue  # the schema check reports an unreadable record
        if not any(doc.get(k) for _, doc in heads.values() for k in MIRROR):
            continue

        def resolve(ref: str) -> str | None:
            if ref in heads:
                return ref
            hits = [h for h in amap.get(ref, []) if h in heads]
            return hits[0] if len(hits) == 1 else None

        remedy = ("restore the links from git (`git log -p` on both files); story links are written only by `record retire`"
                  if kind.name == stories else
                  "restore the links from git (`git log -p` on both files); `decision supersede <old> <new>` writes both sides at once")
        later: dict[str, set[str]] = {}  # each record and the records that supersede it
        for rid, (rel, doc) in sorted(heads.items()):
            for key, back in MIRROR.items():
                for ref in D.as_list(doc.get(key)):
                    target = resolve(ref)
                    if target == rid:
                        out.append(Failure("G-D3", rel, f"{rid} `{key}` names {ref}, itself", remedy))
                    elif target is None:
                        if kind.name != stories:
                            out.append(Failure("G-D3", rel, f"{rid} `{key}` names {ref}, which is no {kind.name} record", remedy))
                    else:
                        if rid not in {resolve(r) for r in D.as_list(heads[target][1].get(back))}:
                            out.append(Failure("G-D3", rel, f"{rid} `{key}` names {target}, but {target} does not name {rid} in `{back}`: the missing side is {target}'s `{back}`", remedy))
                        old, new = (target, rid) if key == "supersedes" else (rid, target)
                        later.setdefault(old, set()).add(new)
        for cycle in _cycles(later):
            rel = heads[cycle[0]][0]
            out.append(Failure("G-D3", rel, f"supersedes links form a cycle: {' -> '.join([*cycle, cycle[0]])} (each is superseded by the next)", remedy))
    return out


def _cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Each cycle of ``graph`` once, as its nodes from the smallest, by depth-first search."""
    found: dict[frozenset[str], list[str]] = {}
    done: set[str] = set()

    def walk(node: str, path: list[str]) -> None:
        if node in path:
            cyc = path[path.index(node):]
            if len(cyc) > 1:
                i = cyc.index(min(cyc, key=key_order_id))
                found.setdefault(frozenset(cyc), cyc[i:] + cyc[:i])
            return
        if node in done:
            return
        for nxt in sorted(graph.get(node, ())):
            walk(nxt, [*path, node])
        done.add(node)

    for start in sorted(graph):
        walk(start, [])
    return list(found.values())


def key_order_id(rid: str) -> tuple[str, int]:
    """An id's sort key: its series, then its number (`DEC-9` before `DEC-10`)."""
    prefix, _, num = rid.rpartition("-")
    return (prefix, int(num) if num.isdigit() else 0)


# -- G-T3 existence in normative text ----------------------------------------------------


def existence(e: Engine) -> list[Failure]:
    """G-T3: in each doc `[guards] existence` lists (criteria, an NFR doc, the residual-risk
    register), every file named in a backticked span, and every `file::symbol`, exists. History
    notes are exempt: blockquotes, and lines carrying `*HISTORY —*`.

    Not checked: names outside backticks, globs and placeholders (`*`, `<`, spaces), paths that
    start with `/` or `.` (commands, extensions), HTTP routes, and whether a cited symbol is the
    definition meant (each dotted part is grepped as a word, as G-D3 does)."""
    out: list[Failure] = []
    files = Files(e.root)
    for rel, path in docs(e.root, e.store.config.guards.existence):
        if path is None:
            out.append(Failure("G-T3", CONFIG_NAME, f"[guards] existence names {rel}, which does not exist", "fix the path, or drop it from [guards] existence"))
            continue
        bad: list[str] = []
        for n, line in prose(_text(path), history=True):
            for span in SPAN_RE.findall(line):
                span = span.strip()
                m = CODE_REF_RE.match(span)
                if m:
                    p = code_ref_problem(files, m["file"], m["symbol"])
                elif PATH_SPAN_RE.match(span) and not span.startswith((".", "/")):
                    p = None if files.find(span) else f"`{span}` does not exist (case-exact)"
                else:
                    continue
                if p:
                    bad.append(f"line {n}: {p}")
        out += [Failure("G-T3", rel, b, "point the text at what exists, or mark a line that is history `*HISTORY —*`") for b in bad]
    return out + decision_code(e, files)


def decision_code(e: Engine, files: Files) -> list[Failure]:
    """G-T3 over the `code:` links of every current decision (`[working] decision`; a
    `status: deprecated` one is history): each file exists case-exact from the repo root and
    names every dotted part of its symbol, by `code_link_problem`, the check `decision link` and
    `decision relink` made when they wrote the link.

    Not checked: a superseded decision's links, and the other link fields (ids: `decision link`
    refuses one that is not a record, and ids are never reused)."""
    if not e.w.decision:
        return []
    out: list[Failure] = []
    st = e.store
    for path in st._files(st.config.kind(e.w.decision)):
        try:
            doc = st.read(path)
        except Exception:
            continue  # the schema check reports an unreadable record
        if doc.get("status") == "deprecated":
            continue
        rel = st._rel(path)
        for link in D.as_list(doc.get("code")):
            problem = code_link_problem(files, link)
            if problem:
                out.append(Failure("G-T3", rel, f"`code:` links `{link}`, but {problem[0]}",f"if the code moved, `decision relink {doc.get('id')} {link} <file::symbol>`; if what it did is gone, `decision supersede` the decision; do not hand-edit `code:`"))
    return out


# -- G-D4 liveness -----------------------------------------------------------------------

WORD_RE = "|".join(LIVENESS)
# a declaration is a line LED by the word (after a blockquote's `>` and emphasis) that opens a block:
# `LIVING. ...`, `**FROZEN 2026-10-12d.**`, `> **FROZEN ...**`. The word in passing ("not a LIVING
# doc"), on a wrapped line, or in fenced code declares nothing, so it cannot pass a doc unread
DECLARED_RE = re.compile(rf"^\s*(?:>\s*)*(?:\*\*|__|\*|_)?({WORD_RE})(?![A-Za-z0-9-])")  # `_FROZEN_` closes with a `_`
FM_LIVENESS_RE = re.compile(r"""^liveness:\s*["']?(.*?)["']?\s*(?:#.*)?$""")  # a frontmatter key, YAML-quoted or not
ARCHIVED_RE = re.compile(r"^\s*ARCHIVED \d{4}-\d{2}-\d{2}")  # an archive's first line (FRAMEWORK §7.3) is FROZEN


@dataclass
class Liveness:
    """What a doc declares near its top: the word (None if nothing), its line, and a problem."""

    word: str | None = None
    line: int = 0
    problem: str = ""


def declared(text: str, window: int) -> Liveness:
    """The first liveness declaration in the first ``window`` lines: a frontmatter `liveness:`
    key, or a line that opens a block (the file's first, or one after a blank line, a heading
    or the frontmatter) led by LIVING, ACTIVE-PLAN or FROZEN, or `ARCHIVED <date>` (FROZEN);
    never fenced code. The topmost wins, because a correction is added at the top (P2)."""
    lines = text.lstrip("\ufeff").split("\n")
    end = None
    if lines and lines[0] == "---":
        end = next((j for j in range(1, len(lines)) if lines[j] == "---"), None)
    fence = False
    for i, line in enumerate(lines[:window]):
        if end is not None and i <= end:
            m = FM_LIVENESS_RE.match(line) if 0 < i < end else None
            if m:
                if m.group(1) in LIVENESS:
                    return Liveness(m.group(1), i + 1)
                return Liveness(None, i + 1, f"line {i + 1}: `liveness: {m.group(1)}` is none of {', '.join(LIVENESS)}")
            continue
        if FENCE_RE.match(line):
            fence = not fence
        if fence or FENCE_RE.match(line):
            continue
        prev = lines[i - 1] if i else ""
        if prev.lstrip(" >").strip() and not HEADING_RE.match(prev) and i != (end if end is not None else -2) + 1:
            continue  # a wrapped line: the word at a soft line break is the word in passing
        if ARCHIVED_RE.match(line):
            return Liveness("FROZEN", i + 1)
        m = DECLARED_RE.match(line)
        if m:
            return Liveness(m.group(1), i + 1)
    return Liveness()


def given(e: Engine) -> tuple[dict[str, tuple[str, str]], list[Failure]]:
    """Each doc `[guards] liveness_given` names, as repo-relative path -> (liveness, glob); and a
    failure for a glob that matches no file (a declaration of nothing has gone stale)."""
    out: dict[str, tuple[str, str]] = {}
    reds: list[Failure] = []
    for glob, word in e.store.config.guards.liveness_given.items():
        hits = sorted(p for p in e.root.glob(glob) if p.is_file())
        if not hits:
            reds.append(Failure("G-D4", CONFIG_NAME, f"[guards] liveness_given names {glob}, which matches no file", "fix the glob, or drop the entry: the doc it declared is gone"))
        for p in hits:
            out.setdefault(p.relative_to(e.root).as_posix(), (word, glob))
    return out, reds


def liveness_of(e: Engine, rel: str, text: str, table: dict[str, tuple[str, str]]) -> str | None:
    """A doc's liveness: its own declaration, else the one `liveness_given` gives it (``table``,
    from `given`). G-D5's banner escape reads it."""
    own = declared(text, e.store.config.guards.liveness_lines).word
    if own:
        return own
    hit = table.get(rel)
    return hit[0] if hit else None


def _board_ids(e: Engine) -> dict[str, bool]:
    """Every board item's id -> whether it is open (not `status: deprecated`)."""
    out: dict[str, bool] = {}
    st = e.store
    for k in e.w.board:
        kind = st.config.kind(k)
        for p in st._files(kind):
            rid = st._id_of(kind, p)
            if rid:
                out[rid] = not _deprecated(_text(p))
    return out


def _under(rel: str, dirs: tuple[str, ...]) -> bool:
    """``rel`` is a listed path or lies under one; `./evidence` and `evidence\\` name `evidence`."""
    norm = [PurePosixPath(d.replace("\\", "/")).as_posix() for d in dirs]
    return any(rel == d or rel.startswith(d + "/") for d in norm)


def liveness(e: Engine) -> list[Failure]:
    """G-D4: every doc under `[guards] liveness` and `history` declares its liveness (P2) in
    its first `liveness_lines` lines (the window): a frontmatter `liveness:` key (YAML quotes
    and a trailing comment allowed; a value that is not a liveness word is red), or a line that
    opens a block (`declared`) led, after a blockquote's `>` and emphasis, by LIVING,
    ACTIVE-PLAN or FROZEN, or by `ARCHIVED <date>` (FROZEN). A doc whose opening lines the repo may
    not edit (frozen provenance, a framework-owned or engine-written file, one signed off by the
    owner) is given its liveness by `liveness_given` instead, and a doc that declares one must agree with
    it. A doc under a `history` directory is FROZEN, or ACTIVE-PLAN while its item is open: with
    `[working] board` set, an ACTIVE-PLAN doc anywhere names a board item in the window, and is
    red only once every board item it names there is closed (freeze it when its item closes, §6.7).
    Red too: a listed path that is missing, a `liveness_given` glob that matches no file, and a
    `liveness` list that yields no doc at all (it would check nothing).

    Not checked: whether the declaration is true (a LIVING doc gone stale is DR9), the change
    mode beside it (P2's other half), files other than `.md` under a listed directory, the word
    in passing (mid-line, on a wrapped line, in fenced code: it declares nothing, so the doc is
    red), indented code, an ACTIVE-PLAN doc whose window also names an open item it does not
    serve, a `liveness_given` glob wide enough to cover every listed doc, which of two globs
    giving one doc different words wins (the first), a floor for `history` (an empty history
    directory is a fresh repo's), and the ACTIVE-PLAN item rule while `[working] board` is
    unset."""
    g = e.store.config.guards
    if not (g.liveness or g.history):
        return []
    table, out = given(e)
    board = _board_ids(e) if e.w.board else None
    seen: set[str] = set()
    read = 0
    for name, paths in (("liveness", g.liveness), ("history", g.history)):
        for rel, path in docs(e.root, paths):
            if path is None:
                out.append(Failure("G-D4", CONFIG_NAME, f"[guards] {name} names {rel}, which does not exist", f"fix the path, or drop it from [guards] {name}"))
                continue
            read += name == "liveness"
            if rel in seen:
                continue
            seen.add(rel)
            text = _text(path)
            own = declared(text, g.liveness_lines)
            give = table.get(rel)
            if own.problem:
                out.append(Failure("G-D4", rel, own.problem, f"write one of {', '.join(LIVENESS)}"))
                continue
            if own.word and give and own.word != give[0]:
                fix = "open it with `ARCHIVED <date>` or a FROZEN line if it is an archived copy (the topmost declaration counts); else " if give[0] == "FROZEN" else ""
                out.append(Failure("G-D4", rel, f"declares {own.word} (line {own.line}), but [guards] liveness_given ({give[1]}) gives it {give[0]}", f"{fix}keep one declaration: make the doc agree, or narrow the liveness_given glob"))
                continue
            word = own.word or (give[0] if give else None)
            if word is None:
                out.append(Failure("G-D4", rel, f"declares no liveness in its first {g.liveness_lines} lines", f"open it with a line led by {', '.join(LIVENESS)}, or a frontmatter `liveness:` key (FRAMEWORK P2); a doc whose opening lines this repo may not edit (frozen provenance, a framework-owned file) goes in [guards] liveness_given"))
                continue
            if word == "LIVING" and _under(rel, g.history):
                out.append(Failure("G-D4", rel, "is LIVING, but it sits in a history directory ([guards] history), which holds provenance", "freeze it (a FROZEN line at the top), or mark it ACTIVE-PLAN while its item is open; a doc kept current belongs outside the history directory"))
            if word == "ACTIVE-PLAN" and board is not None:
                named = list(_named(text, g.liveness_lines, board))
                if not named:
                    out.append(Failure("G-D4", rel, f"is ACTIVE-PLAN but names no board item in its first {g.liveness_lines} lines, so nobody can tell when its item closes", "name the item it serves near the top (FRAMEWORK §7.2), or freeze it"))
                elif not any(board[i] for i in named):
                    out.append(Failure("G-D4", rel, f"is ACTIVE-PLAN, but every item it names ({', '.join(named)}) is closed", "freeze it: a FROZEN line with the date at the top, above the ACTIVE-PLAN one (FRAMEWORK §6.7)"))
    if g.liveness and read == 0:
        out.append(Failure("G-D4", CONFIG_NAME, f"[guards] liveness ({', '.join(g.liveness)}) holds no doc, so G-D4 checks nothing there", "list the docs to check, or empty the list"))
    return out


def _named(text: str, window: int, board: dict[str, bool]) -> dict[str, bool]:
    """The board items an ACTIVE-PLAN doc names in its window, each -> whether it is open."""
    top = "\n".join(text.lstrip("\ufeff").split("\n")[:window])
    return {i: board[i] for i in dict.fromkeys(ID_RE.findall(top)) if i in board}


def active_plans(e: Engine) -> list[tuple[str, dict[str, bool]]]:
    """Each doc G-D4 reads (`[guards] liveness` and `history`) whose liveness is ACTIVE-PLAN, as
    (repo-relative path, the board items its window names -> open), read as `liveness` reads
    it. `task close` reads it (CE-27): closing the last open item a plan names would turn G-D4
    red, so the close refuses until the plan is frozen (`doc freeze`). Empty while G-D4 reads
    nothing or `[working] board` is unset."""
    g = e.store.config.guards
    if not (g.liveness or g.history) or not e.w.board:
        return []
    table, _ = given(e)
    board = _board_ids(e)
    out: list[tuple[str, dict[str, bool]]] = []
    seen: set[str] = set()
    for rel, path in docs(e.root, (*g.liveness, *g.history)):
        if path is None or rel in seen:
            continue
        seen.add(rel)
        text = _text(path)
        own = declared(text, g.liveness_lines)
        word = own.word or (table[rel][0] if rel in table else None)
        if word == "ACTIVE-PLAN" and not own.problem:
            out.append((rel, _named(text, g.liveness_lines, board)))
    return out


# -- G-D5 typed numbers ------------------------------------------------------------------

SPELLED = "three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty"
# a number: a numeral, or a spelled one from three up ("one test" and "two checks" are narrative far
# more often than a census); never mid-token (`R6`, `1.5`, `§6`, `G-D5`, `#3`, `a/3`)
COUNT_NUMBER = rf"(?<![\w.,\-§#/])(?:\d+(?:,\d{{3}})*|{SPELLED})"
COUNT_ADJ = r"(?:(?:open|closed|new)\s+)?"  # `12 open tasks`
DATED_RE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")  # a date or session key anywhere on the line, a file name's too (P5)
QUOTED_RE = re.compile("`[^`\n]*`|\"[^\"\n]*\"|“[^”\n]*”")  # a backticked or quoted span (P5)
# a bound is a rule's value, not a count of things in the tree: `at most 2 entries`, `more than 3 tasks`
BOUND_RE = re.compile(r"(?:at most|at least|more than|fewer than|less than|up to)\s*$", re.IGNORECASE)


def count_re(nouns: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile(rf"{COUNT_NUMBER}\s+{COUNT_ADJ}(?:{'|'.join(map(re.escape, nouns))})(?![\w-])", re.IGNORECASE)


def typed_counts(text: str, nouns: tuple[str, ...]) -> list[tuple[int, str]]:
    """(line number, the count) for each hand-typed count of things in the tree: a number directly
    before a counted noun (an `open`, `closed` or `new` between them allowed), outside P5's
    other forms: fenced code (and frontmatter), a backticked or quoted span, a line carrying a
    `YYYY-MM-DD` key; and not a bound (`at most N`), which is a rule's value."""
    rx = count_re(nouns)
    out: list[tuple[int, str]] = []
    for n, line in prose(text.lstrip("\ufeff")):  # an editor's BOM must not hide the frontmatter
        if DATED_RE.search(line):
            continue
        bare = QUOTED_RE.sub(lambda m: " " * len(m.group(0)), line)
        for m in rx.finditer(bare):
            if not BOUND_RE.search(bare[: m.start()]):
                out.append((n, re.sub(r"\s+", " ", m.group(0))))
    return out


def numbers(e: Engine) -> list[Failure]:
    """G-D5: in each doc `[guards] numbers` lists, no count of things in the tree is typed in prose (P5):
    a number (a numeral, or a spelled one from three to twenty) directly before a noun of
    `[guards] count_nouns` (`23 components`, `12 open tasks`), case-insensitive. A number glued
    on its left to a letter, digit, `.`, `,`, `-`, `§`, `#` or `/` is part of a token (`R6`,
    `1.5`, `§6`, `G-D5`) and counts for nothing. P5's four forms pass: fenced code (and
    frontmatter), a backticked or double-quoted span, a line with a `YYYY-MM-DD` anywhere on it
    (a dated measurement), and a doc whose liveness is FROZEN or ACTIVE-PLAN (its body is
    provenance; G-D4's reader, so `liveness_given` counts). A bound (`at most 2 entries`, `more
    than 3 tasks`) is a rule's value, not a count, and passes. Red too: a listed path that is
    missing, and a list whose docs are all FROZEN or ACTIVE-PLAN or none (it would check
    nothing).

    Not checked: counts of nouns not in `count_nouns`, singulars, an adjective other than
    `open`, `closed` or `new` between number and noun (`four method runbooks`), emphasis or a
    sign on the number (`**23**`, `23+`), spelled numbers outside three to twenty, a count split
    across a line break, a single-quoted span (scanned), whether a dated number is still true
    (P5: re-measure), a FROZEN or ACTIVE-PLAN word G-D4 does not check (list each `numbers` doc
    under `liveness` too), and generated blocks inside a hand-written doc (no generator writes
    one yet). Red although no count: a rule's value without a bound word (`the last 5 entries`)
    and a label (`Step 3 checks`); the remedy is backticks."""
    g = e.store.config.guards
    if not g.numbers:
        return []
    out: list[Failure] = []
    table = given(e)[0]
    scanned = 0
    for rel, path in docs(e.root, g.numbers):
        if path is None:
            out.append(Failure("G-D5", CONFIG_NAME, f"[guards] numbers names {rel}, which does not exist", "fix the path, or drop it from [guards] numbers"))
            continue
        text = _text(path)
        if liveness_of(e, rel, text, table) in ("FROZEN", "ACTIVE-PLAN"):
            continue
        scanned += 1
        out += count_failures(rel, text, g.count_nouns)
    if scanned == 0 and not out:
        out.append(Failure("G-D5", CONFIG_NAME, f"[guards] numbers ({', '.join(g.numbers)}) holds no doc that is not FROZEN or ACTIVE-PLAN, so G-D5 checks nothing", "list the LIVING docs, or empty the list to switch G-D5 off"))
    return out


def count_failures(rel: str, text: str, nouns: tuple[str, ...]) -> list[Failure]:
    """G-D5 on one doc's text: lint's check, and a write's (CE-63)."""
    return [Failure("G-D5", rel, f"line {n}: `{count}` is a hand-typed count of things in the tree", "delete the number and point at its home (the command, table or file that counts it; P5); a measurement keeps its YYYY-MM-DD on the line; a quoted figure, a rule's value or a label (`Step 3 checks`) goes in backticks")
            for n, count in typed_counts(text, nouns)]


# -- G-D7 signal budgets -----------------------------------------------------------------


def signals(e: Engine) -> list[Failure]:
    """G-D7: in each doc `[guards] signals` lists, at most `warn_max` ⚠ and `bold_caps_max` bold
    all-caps spans (`**NEVER**`: a bold span with a run of four capitals and no lower case), and
    no glyph from `retired_glyphs`. A signal stands out only while it is rare.

    Not checked: fenced code, other emphasis (italics, `!`), and whether a signal is deserved."""
    g = e.store.config.guards
    out: list[Failure] = []
    for rel, path in docs(e.root, g.signals):
        if path is None:
            out.append(Failure("G-D7", CONFIG_NAME, f"[guards] signals names {rel}, which does not exist", "fix the path, or drop it from [guards] signals"))
            continue
        body = "\n".join(line for _, line in prose(_text(path)))
        warns = body.count(WARN)
        if warns > g.warn_max:
            out.append(Failure("G-D7", rel, f"{warns} {WARN} signals (at most {g.warn_max})", f"keep {WARN} for the few traps that cost the most; demote the rest to plain text"))
        caps_ = BOLD_CAPS_RE.findall(body)
        if len(caps_) > g.bold_caps_max:
            out.append(Failure("G-D7", rel, f"{len(caps_)} bold all-caps spans (at most {g.bold_caps_max}; the first: {caps_[0]})", "keep bold capitals for the few rules that must never break; write the rest in sentence case"))
        for glyph in g.retired_glyphs:
            if glyph in body:
                out.append(Failure("G-D7", rel, f"uses the retired glyph {glyph!r}", "replace it with words or a current signal"))
    return out


# -- G-D8 the orientation note's stacking check -------------------------------------------


def note_layers(e: Engine) -> list[Failure]:
    """G-D8: the orientation note has at most one `## Banner (<key>)` heading (G-W1 asks for
    one), no other heading carries a session key (a session's section, or a ledger entry heading
    pasted in), and no bullet or bold lead in the banner is a session key (a session's stacked update).

    Not checked: session keys inside a sentence (dated facts cite them as provenance), the
    banner's size (G-D1 on the orientation note's route), and an inline board's position: the board is one
    file per item, read with `task list`."""
    rel = e.w.handoff
    path = e.root / rel if rel else None
    if path is None or not path.is_file():
        return []
    return layer_failures(rel, _text(path))


def layer_failures(rel: str, text: str) -> list[Failure]:
    """G-D8 on the orientation note's text: lint's check, and a write's (CE-63)."""
    out: list[Failure] = []
    banners = L.BANNER_RE.findall(text)
    if len(banners) > 1:
        out.append(Failure("G-D8", rel, f"{len(banners)} banner headings ({', '.join(banners)})", "keep the newest; `banner set` replaces the banner, it never adds one"))
    key_head = re.compile(rf"^#+ .*\b{KEY_RE}\b")
    stacked = [line for _, line in prose(text) if key_head.match(line) and not L.BANNER_RE.match(line)]
    if stacked:
        out.append(Failure("G-D8", rel, f"{len(stacked)} headings carry a session key (the first: {stacked[0].strip()!r}): session history in the orientation note", "move it to the ledger, or into the one banner; the orientation note is replaced, not stacked"))
    b = L.find_banner(text)
    if b is not None:
        lead = re.compile(rf"^\s*(?:(?:[-*+]|\d+\.)\s+\**|\*\*)\s*{KEY_RE}\b")  # a bullet or bold lead, not a wrapped line
        stacked = [ln for ln in b.text.split("\n") if lead.match(ln)]
        if stacked:
            out.append(Failure("G-D8", rel, f"{len(stacked)} banner lines start with a session key (the first: {stacked[0].strip()[:60]!r}): a stacked banner", "rewrite the banner as what is true now, under its one key; history goes in the ledger"))
    return out


# -- G-D9 provenance on tuned values -----------------------------------------------------


@dataclass
class Tuned:
    line: int
    key: str
    problem: str = ""


def provenance_problems(text: str) -> list[Tuned]:
    """Every number a context.toml text assigns (inline tables included), and what is wrong with
    the provenance note on its line."""
    out: list[Tuned] = []
    for n, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        code, _, note = STRING_RE.sub('""', line).partition("#")
        for key in NUMBER_KEY_RE.findall(code):
            t = Tuned(n, key)
            if not PROVENANCE_RE.search(note):
                t.problem = "has no `provenance: MEASURED` or `provenance: JUDGEMENT` note"
            elif not re.search(r"wrong if|wrong as above", note):
                t.problem = "says nothing about what would make it wrong (`wrong if ...`)"
            elif re.search(r"\bexample", note, re.IGNORECASE):
                t.problem = "cites an example as its provenance: a spec example is not a measurement or a judgement"
            out.append(t)
    return out


def provenance(e: Engine) -> list[Failure]:
    """G-D9: every number in context.toml (a cap, a budget, a window, a timeout) carries, on its
    own line, `provenance: MEASURED` or `provenance: JUDGEMENT`, the method, and `wrong if ...`
    (`wrong as above` for a run of lines); a note citing an example is refused (§8.0).

    Not checked: whether the note is true, values the file leaves at the engine default (the
    kit's template carries their provenance), and non-numeric settings."""
    path = e.root / CONFIG_NAME
    if not path.is_file():
        return []
    return [
        Failure("G-D9", CONFIG_NAME, f"`{t.key}` (line {t.line}) {t.problem}", "add `# provenance: MEASURED <date, method>` or `JUDGEMENT <why>`, then `; wrong if <what would show it is wrong>`")
        for t in provenance_problems(_text(path))
        if t.problem
    ]


# -- G-W7 tool-owned frontmatter ---------------------------------------------------------

SESSION_OWNED = ("moved", "updated", "closed", "last_asked")


def tool_owned(e: Engine) -> list[Failure]:
    """G-W7 on the stored files: every session-keyed tool-owned key of a board item (`moved`, `updated`,
    `closed`, `last_asked`) names the session of the newest logged operation that wrote it; a
    value no operation wrote must be older than the op log's first entry (written before the
    engine ran the board). Every op log line parses.

    Not checked: the values of `state`, `pri` and `deps` (the log records which keys changed,
    not their values; `task set` refuses them at write time), and keys of kinds off the board."""
    if not e.w.board:
        return []
    ops = _ops(e)
    out: list[Failure] = []
    log_rel = e.store.config.oplog
    bad = [n for n, op in ops if not isinstance(op, dict)]
    if bad:
        out.append(Failure("G-W7", log_rel, f"{len(bad)} lines do not parse as JSON (the first: line {bad[0]})", "restore them from git; the op log is written only by the engine"))
    good = [op for _, op in ops if isinstance(op, dict)]
    first = min((str(op.get("session")) for op in good if op.get("session")), key=key_order, default=None)
    newest: dict[tuple[str, str], dict] = {}
    for op in good:
        for k in op.get("fields") or ():
            if k in SESSION_OWNED:
                newest[(str(op.get("id")), k)] = op
    for r in e.board_heads():
        rel = r.path.relative_to(e.root).as_posix()
        for k in SESSION_OWNED:
            v = r.doc.get(k)
            if v in (None, ""):
                continue
            v = str(v)
            op = newest.get((r.id, k))
            if op is not None:
                if v != str(op.get("session")):
                    out.append(Failure("G-W7", rel, f"`{k}: {v}`, but the newest operation that wrote it ({op.get('op')}, {op.get('at', '?')}) was in session {op.get('session')}", f"restore `{k}` from git: {k} is changed only by an operation (manual-mode.md § What every write does)"))
            elif first is None or not re.fullmatch(KEY_RE, v) or key_order(v) >= key_order(first):
                out.append(Failure("G-W7", rel, f"`{k}: {v}`, but no logged operation wrote it", f"restore `{k}` from git, or redo the change with the operation that owns it"))
    return out


def op_records(e: Engine) -> list[Failure]:
    """G-W7 on the op log's records (CE-54, INV-44): every op line that wrote a record of a
    configured kind (its `id` in a kind's series) names, in `path`, a file that is in the tree. The
    engine commits an op line with the files it names, but a by-hand commit can carry the op log
    alone, and then a clean checkout holds a write whose record is not there. One failure per
    missing path, naming its first line.

    Not checked: op lines of what is not a record (the banner, the ledger, an index, the register:
    their files are routes, G-R1's), a `doc.archive` line (it names the path it moved away from),
    whether the file at the path is the record the line names (ids are in file names, G-D2), and a
    record committed later than its op line (a commit's own state: `context-engine commit` takes
    them together)."""
    st = e.store
    seen: dict[str, tuple[int, dict, int]] = {}
    for n, op in _ops(e):
        if not isinstance(op, dict) or op.get("op") == "doc.archive":
            continue
        rel, rid = op.get("path"), str(op.get("id") or "")
        if not isinstance(rel, str) or not rel or not any(k.id_re.match(rid) for k in st.config.kinds.values()):
            continue
        if rel in seen:
            first, line, count = seen[rel]
            seen[rel] = (first, line, count + 1)
        elif not (e.root / rel).is_file():
            seen[rel] = (n, op, 1)
    return [
        Failure("G-W7", st.config.oplog,
                f"line {n} ({op.get('op')} {op.get('id')}, session {op.get('session')})" + (f" and {count - 1} more name" if count > 1 else " names") + f" {rel}, which is not in the tree: the op line was committed without the record it wrote",
                f"restore {rel} from the working copy or commit that has it and commit it by path with its op line (manual-mode.md § context-engine commit); never delete an op line")
        for rel, (n, op, count) in seen.items()
    ]


# -- G-D12 framework coverage ------------------------------------------------------------

# What G-D12 extracts from the spec, each class with its floor: fewer than the floor means the
# spec's format changed under the pattern, so the class is red rather than silently unchecked.
# Floors: provenance: JUDGEMENT, CE-30; FRAMEWORK.md held 23 components, 14 procedures (then called
# rituals) and 41 G-ids on 2026-10-13a (counted by these patterns); wrong if the spec is trimmed
# below them on purpose.
COMPONENT_SECTION_RE = re.compile(r"^##\s+2\.\s")  # §2 "The components at a glance": its table
COMPONENT_RE = re.compile(r"^\|\s*\d+\s*\|[^|]*\|\s*\*\*(?P<name>[^*|]+?)\*\*")  # `| 1 | Intent | **Charter** |`
PROCEDURE_RE = re.compile(r"^###\s+(?P<num>5\.6|6\.\d+)\s+(?P<name>.+?)\s*$")  # `### 6.1 Session start`
GID_RE = re.compile(r"(?<![\w-])G-[A-Z]\d+(?!\w)")  # `G-D3`
COVERAGE_FLOORS = {"component": 20, "procedure": 10, "G-id": 30}
MAP_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})([a-z]*)")
# Where a coverage map's table owns each class: (the headers, any one of which marks the table; the
# header of the column holding the key). A component row's `§` cell is not a procedure, nor is a
# guard row's. `Ritual` is the procedures' old name (DEC-39): frozen maps keep it, new maps say
# `Procedure`, and both count.
MAP_COLUMNS = {"component": (("Component",), "Component"), "procedure": (("Procedure", "Ritual"), "§"), "G-id": (("Guard",), "Guard")}
# A §2 component's earlier names (DEC-39), so a frozen map's row under the old name still owns it.
COMPONENT_ALIASES = {
    "Residual-risk register": ("Invariants",),
    "Non-functional requirements (NFRs)": ("Law / NFRs",),
    "Non-functional requirements": ("Law / NFRs",),
}


@dataclass(frozen=True)
class Owned:
    """One thing the spec names that something must own: its class, its key, and how to name it."""

    cls: str
    key: str  # a component's name, `§6.4`, or `G-D3`
    label: str

    def names(self) -> tuple[str, ...]:
        """The key, then a component's earlier names (`COMPONENT_ALIASES`)."""
        return (self.key, *COMPONENT_ALIASES.get(self.key, ())) if self.cls == "component" else (self.key,)

    def in_cell(self, cell: str) -> bool:
        """A map row names it: the cell is the key or an earlier name (a component's cell may add a
        parenthesis)."""
        return any(cell == n or (self.cls == "component" and cell.startswith(n + " (")) for n in self.names())

    def in_text(self, text: str) -> bool:
        """A board item names it: the key or an earlier name as a word (`§6.1` is not `§6.13`;
        `G-D1` is not `G-D10`)."""
        return any(re.search(rf"(?<![\w-]){re.escape(n)}(?!\w|\.\d)", text) is not None for n in self.names())


def spec_items(text: str) -> dict[str, list[Owned]]:
    """Every component (§2's table), procedure (§5.6 and §6.n headings) and G-id the spec names, by
    class, outside fenced code; each key once, in order of first appearance."""
    out: dict[str, list[Owned]] = {c: [] for c in COVERAGE_FLOORS}
    seen: set[tuple[str, str]] = set()

    def add(item: Owned) -> None:
        if (item.cls, item.key) not in seen:
            seen.add((item.cls, item.key))
            out[item.cls].append(item)

    section = False
    for _, line in prose(text):
        h = HEADING_RE.match(line)
        if h and len(h.group(1)) <= 2:
            section = bool(COMPONENT_SECTION_RE.match(line))
        m = COMPONENT_RE.match(line)
        if section and m:
            name = m["name"].strip()
            add(Owned("component", name, f"component {name!r} (§2)"))
        m = PROCEDURE_RE.match(line)
        if m:
            add(Owned("procedure", f"§{m['num']}", f"procedure §{m['num']} {m['name']!r}"))
        for gid in GID_RE.findall(line):
            add(Owned("G-id", gid, f"guard {gid}"))
    return out


def coverage_maps(root: Path, pattern: str) -> tuple[list[Path], list[Path]]:
    """(the maps the repo-relative glob matches, newest first by the date and session letters in
    the file name, ordered as session keys are (`z` before `aa`); the matches with no date in
    their name)."""
    dated, undated = [], []
    for p in root.glob(pattern):
        if p.is_file():
            (dated if MAP_DATE_RE.search(p.name) else undated).append(p)
    dated.sort(key=lambda p: (key_order("".join(MAP_DATE_RE.search(p.name).groups())), p.name), reverse=True)
    return dated, sorted(undated)


def map_cells(text: str) -> dict[str, set[str]]:
    """By class, the stripped cells of a coverage map's tables that can own it: in each table
    whose header row has one of the class's marking headers, the cells under its key column
    (`MAP_COLUMNS`)."""
    out: dict[str, set[str]] = {c: set() for c in MAP_COLUMNS}
    header: list[str] | None = None
    last = -2
    for n, line in prose(text):
        row = line.strip()
        if not row.startswith("|") or n != last + 1:
            header = None
        last = n
        if not row.startswith("|"):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells):  # the |---| separator
            continue
        for cls, (marks, column) in MAP_COLUMNS.items():
            if any(m in header for m in marks) and column in header and header.index(column) < len(cells):
                out[cls].add(cells[header.index(column)])
    return out


def coverage(e: Engine) -> list[Failure]:
    """G-D12: every component (§2's table), procedure (§5.6, §6.n headings) and G-id the spec
    (`[guards] coverage_spec`) names is owned: a table row of the newest coverage map
    (`[guards] coverage_maps`, a repo-relative glob; newest by the date and session letters in
    the file name) names it in its class's key column (`MAP_COLUMNS`: `Component`; `§` in a
    table with a `Procedure` or `Ritual` column; `Guard`), or a board item, open or closed,
    names it; a component's earlier name (`COMPONENT_ALIASES`) counts as its name. Red when
    a class extracts fewer than its floor (`COVERAGE_FLOORS`), so a reworded format cannot pass
    by finding nothing; when only one of the two keys is set; when the spec is missing; when the
    glob is not repo-relative or matches nothing; and when a matching map has no date in its name.

    Not checked: whether a board item's mention is ownership or a passing reference (a
    judgement; the map's one-class-per-table layout carries it), whether a map row's class is
    right, the rest of the spec (§3, §7 and §9 are context), and maps other than the newest."""
    g = e.store.config.guards
    if not (g.coverage_spec or g.coverage_maps):
        return []
    off = 'or switch G-D12 off (`[guards] off = ["G-D12"]`, or unset both coverage_spec and coverage_maps)'
    if not (g.coverage_spec and g.coverage_maps):
        have, need = ("coverage_spec", "coverage_maps") if g.coverage_spec else ("coverage_maps", "coverage_spec")
        return [Failure("G-D12", CONFIG_NAME, f"[guards] sets {have} but not {need}", f"set {need} too, {off}")]
    out: list[Failure] = []
    spec = e.root / g.coverage_spec
    if not spec.is_file():
        out.append(Failure("G-D12", CONFIG_NAME, f"[guards] coverage_spec names {g.coverage_spec}, which does not exist", f"fix the path, {off}"))
    glob = PureWindowsPath(g.coverage_maps)  # reads `/` and `\` alike: a root or a drive on either OS is an anchor
    if glob.anchor or ".." in glob.parts:
        out.append(Failure("G-D12", CONFIG_NAME, f"[guards] coverage_maps ({g.coverage_maps}) is not a glob relative to the repo root", f"make it repo-relative with no `..` (e.g. docs/evidence/framework-coverage-*.md), {off}"))
        return out
    maps, undated = coverage_maps(e.root, g.coverage_maps)
    for p in undated:
        out.append(Failure("G-D12", p.relative_to(e.root).as_posix(), "matches [guards] coverage_maps but has no date (YYYY-MM-DD) in its name, so the engine cannot tell which map is newest", "rename it with its date, or narrow the coverage_maps glob"))
    if not maps and not undated:
        out.append(Failure("G-D12", CONFIG_NAME, f"[guards] coverage_maps matches no file ({g.coverage_maps})", f"fix the glob, {off}"))
    if out:
        return out
    items = spec_items(_text(spec))
    for cls, floor in COVERAGE_FLOORS.items():
        if len(items[cls]) < floor:
            out.append(Failure("G-D12", g.coverage_spec, f"{len(items[cls])} {cls}s extracted, under the floor of {floor}: the spec's format no longer matches the pattern, so they would go unchecked", "the patterns and floors are the engine's (guards.py: COMPONENT_RE, PROCEDURE_RE, GID_RE, COVERAGE_FLOORS) and fit FRAMEWORK.md's format: change them in the engine with a provenance note if FRAMEWORK changed on purpose; a repo whose spec they do not fit switches G-D12 off (`[guards] off = [\"G-D12\"]`, or unset both coverage_spec and coverage_maps)"))
    if out:
        return out
    map_rel = maps[0].relative_to(e.root).as_posix()
    cells = map_cells(_text(maps[0]))
    board = [_text(p) for p in sorted({p for k in e.w.board for p in e.store._files(e.store.config.kind(k))})]  # tasks and questions may share a directory
    for cls in COVERAGE_FLOORS:
        for item in items[cls]:
            if not any(item.in_cell(c) for c in cells[cls]) and not any(item.in_text(t) for t in board):
                out.append(Failure("G-D12", g.coverage_spec, f"{item.label} is owned by no row of {map_rel} and named by no board item", f"file a board item that names {item.key} (`task new`), or write a new dated coverage map with a row for it; the map is frozen, never edit it"))
    return out


# -- the correctness chain: G-I1, G-I2, G-T1, G-T2, G-T6 (CE-25) --------------------------

ID_FORM = r"[A-Z]+-[1-9][0-9]*"  # every id the framework mints: a capital prefix, a dash, a number (FRAMEWORK P3)
# An id in the stored files is read verbatim, so one stamped before a repo took up the form (`ADR-0007`)
# still resolves (P3); the store's ids are `prefix-digits` too (config.py::Kind.id_re).
READ_FORM = r"[A-Z]+-[0-9]+"
ID_RE = re.compile(rf"(?<![\w-]){READ_FORM}(?![\w-])")
ROW_ID_RE = re.compile(READ_FORM)  # a criterion row's whole first cell: the rows working.py::CRITERION_ROW_RE reads
PIPE_RE = re.compile(r"(?<!\\)\|")  # a cell boundary; a GFM-escaped `\|` stays inside its cell
GOAL_RE = re.compile(r"G-?([1-9][0-9]*)")  # `G-3`, and the legacy `G3` of records written before the standard id form
STORY_STATUSES = ("live", "unspecified", "unconfirmed", "retired")  # FRAMEWORK §3.2
CRITERION_STATUSES = ("planned", "tested", "manual", "deviates", "retired")  # FRAMEWORK §3.3
CLAIMED = ("tested", "manual")  # the statuses G-T2 requires a claim for
AGENT_ACTOR_RE = re.compile(r"agent \([^()]*reconstructed from .+\)")
STORY_ACTOR_RE = re.compile(rf"owner|human:\S+|{AGENT_ACTOR_RE.pattern}")  # FRAMEWORK §3.2
RETIRE_BY_RE = re.compile(r"owner|human:\S+|agent")  # whose call a `record retire` is (FRAMEWORK §3.2)
RETIRE_KEYS = ("supersedes", "superseded_by")  # a story's links: only `record retire` writes them
CONFIRM_BY_RE = re.compile(r"owner|human:\S+")  # whose words a `record confirm` records: never an agent's (FRAMEWORK §3.2)
CONFIRMED = ("live", "unspecified")  # what `record confirm` makes an agent's reconstruction (FRAMEWORK §3.2)
SOURCE_COLUMNS = ("from", "story", "source")  # a criteria table's source column, by its header
INTENT_OFF = "unset it in [guards] to switch the guard off"


def goal_id(text: str) -> str | None:
    """A goal id in the standard id form (`G-3`), from `G-3` or the legacy `G3`; None if it is not one."""
    m = GOAL_RE.fullmatch(text.strip().strip("*`").strip())
    return f"G-{m.group(1)}" if m else None


def tables(text: str) -> Iterator[tuple[list[str], list[tuple[int, list[str]]]]]:
    """Each markdown table outside fenced code: (its header cells, lower-cased; its body rows as
    (line number, stripped cells)). The `|---|` separator is skipped."""
    header: list[str] | None = None
    body: list[tuple[int, list[str]]] = []
    last = -2
    for n, line in prose(text):
        row = line.strip()
        if not row.startswith("|") or n != last + 1:
            if header is not None:
                yield header, body
            header, body = None, []
        last = n
        if not row.startswith("|"):
            continue
        inner = row[1:-1] if len(row) > 1 and row.endswith("|") and not row.endswith("\\|") else row[1:]
        cells = [c.strip() for c in PIPE_RE.split(inner)]
        if header is None:
            header = [c.lower() for c in cells]
        elif not all(set(c) <= set("-: ") for c in cells):
            body.append((n, cells))
    if header is not None:
        yield header, body


def charter_goals(text: str) -> tuple[list[tuple[int, str, str]], list[tuple[int, str]]]:
    """(line number, goal id, the cell as written) for each table row the charter leads with a
    goal id, in the standard form or the legacy one (`goal_id`); and (line number, first cell) of each
    other row of a table that has goal rows: no goal, and it must not pass unread."""
    found: list[tuple[int, str, str]] = []
    strays: list[tuple[int, str]] = []
    for _, body in tables(text):
        mine = [(n, cells[0], goal_id(cells[0])) for n, cells in body]
        if any(gid for _, _, gid in mine):
            found += [(n, gid, raw) for n, raw, gid in mine if gid]
            strays += [(n, raw) for n, raw, gid in mine if not gid]
    return found, strays


@dataclass(frozen=True)
class Criterion:
    """One row of the criteria file: its id, line, source cell (`from`) and status, lower-cased."""

    id: str
    line: int
    source: str
    status: str


def criteria_rows(text: str) -> tuple[list[Criterion], list[tuple[str, str]]]:
    """The criterion rows (a table row whose whole first cell is an id, `ROW_ID_RE`), and the
    problems, as (message, remedy), that stop a row being read: a table of criteria with no
    `status` column or no source column (`from`, `story` or `source`), and a row of a table of
    criteria not led by a plain id (`**AC-4**`, `AC 6`), which would otherwise pass unread."""
    rows: list[Criterion] = []
    problems: list[tuple[str, str]] = []
    for header, body in tables(text):
        mine = [(n, cells) for n, cells in body if ROW_ID_RE.fullmatch(cells[0])]
        if not mine:
            continue
        for n, cells in body:
            if not ROW_ID_RE.fullmatch(cells[0]):
                problems.append((f"line {n}: a row of a table of criteria is led by `{cells[0]}`, which is not an id, so the row is not read", "lead the row with its id alone and plain (`| AC-4 | ...`), or move the line out of the table (FRAMEWORK §3.3)"))
        src = next((header.index(c) for c in SOURCE_COLUMNS if c in header), None)
        status = header.index("status") if "status" in header else None
        if src is None or status is None:
            missing = "source column (`from`, `story` or `source`)" if src is None else "`status` column"
            problems.append((f"line {mine[0][0]}: a table of criteria has no {missing}, so its {len(mine)} rows cannot be read", "give the table its `status` and `from` columns (FRAMEWORK §3.3)"))
            continue
        for n, cells in mine:
            src_cell = cells[src] if src < len(cells) else ""
            status_cell = cells[status] if status < len(cells) else ""
            rows.append(Criterion(cells[0], n, src_cell, status_cell.strip("`*").strip().lower()))
    return rows, problems


def story_problems(doc) -> list[str]:
    """G-I2 on one story's frontmatter: an actor of the vocabulary, a date, a status of the
    vocabulary, and `unconfirmed` only from an agent's reconstruction. `record new` calls it too.
    A retired story is history: its provenance is not read (`record retire` replaced a story
    with bad provenance by its replacement story, a new record with the same words), and its
    retirement is `retire_problems`' to check."""
    if str(doc.get("story_status") or "") == "retired":
        return []
    out = []
    actor = str(doc.get("actor") or "")
    if not STORY_ACTOR_RE.fullmatch(actor):
        out.append(f"`actor: {actor}` is none of `owner`, `human:<id>` or `agent (reconstructed from ...)`")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(doc.get("date") or "")):
        out.append(f"`date: {doc.get('date') or ''}` is not a date (YYYY-MM-DD)")
    status = str(doc.get("story_status") or "")
    if status not in STORY_STATUSES:
        out.append(f"`story_status: {status}` is none of {', '.join(STORY_STATUSES)}")
    elif status == "unconfirmed" and not AGENT_ACTOR_RE.fullmatch(actor):
        out.append(f"`unconfirmed` is for a story an agent reconstructed, but its actor is `{actor}`")
    return out


def goal_problems(goals, known: set[str], legacy: bool = True) -> list[str]:
    """G-I1 on one story's or open task's `goals`: at least one, each a goal of the charter (`known`). A legacy
    `G3` reads as `G-3` in the stored files (``legacy``); a new write must use the standard form. `record new`
    calls it too."""
    values = D.as_list(goals)
    if not values:
        return ["names no goal (`goals` is empty)"]
    out = []
    for v in values:
        gid = goal_id(v)
        if gid is None:
            out.append(f"`{v}` in `goals` is not a goal id (G-n)")
        elif not legacy and v != gid:
            out.append(f"`{v}` in `goals` is not in the standard id form; write {gid}")
        elif gid not in known:
            out.append(f"`goals` names {gid}, which is not a goal of the charter")
    return out


def _stories(e: Engine) -> list[tuple[str, str, object]]:
    """(id, repo-relative path, frontmatter) of each story record (`[guards] stories`)."""
    st = e.store
    kind = st.config.kind(st.config.guards.stories)
    out = []
    for path in st._files(kind):
        rid = st._id_of(kind, path)
        if rid is None:
            continue
        try:
            out.append((rid, st._rel(path), st.read(path)))
        except Exception:
            continue  # the schema check reports an unreadable record
    return out


def known_goals(e: Engine) -> tuple[set[str] | None, list[Failure]]:
    """The charter's goal ids (None when `[guards] charter` is unset), and G-I1's failures on the
    charter itself: missing, no goal rows (the table changed under the pattern), a legacy id, a
    goal id leading two rows."""
    rel = e.store.config.guards.charter
    if not rel:
        return None, []
    path = e.root / rel
    if not path.is_file():
        return set(), [Failure("G-I1", CONFIG_NAME, f"[guards] charter names {rel}, which does not exist", f"fix the path, or {INTENT_OFF}")]
    out: list[Failure] = []
    found, strays = charter_goals(_text(path))
    for n, raw in strays:
        out.append(Failure("G-I1", rel, f"line {n}: a row of the goal table is led by `{raw}`, which is not a goal id, so the row is not read as a goal", "lead each goal's row with its id in the standard form, G-n (FRAMEWORK P3), or move the row out of the goal table"))
    if not found:
        out.append(Failure("G-I1", rel, "no goal rows: no table row starts with a goal id (`| G-1 | ... |`), so no story's goals can be checked", f"give each goal a row led by its id, G-n (FRAMEWORK §3.1), or {INTENT_OFF}"))
    seen: set[str] = set()
    for n, gid, raw in found:
        if raw.strip("*`").strip() != gid:
            out.append(Failure("G-I1", rel, f"line {n}: goal id {raw} is not in the standard id form", f"write it {gid} (FRAMEWORK P3); a story's `goals` may keep the legacy {raw}, which reads as {gid}"))
        if gid in seen:
            out.append(Failure("G-I1", rel, f"line {n}: goal id {gid} leads two rows", "give the newer goal the next free id (ids are never reused, P3)"))
        seen.add(gid)
    return seen, out


def goals(e: Engine) -> list[Failure]:
    """G-I1: every goal of the charter (`[guards] charter`) is named by a story that is not
    retired, and every such story names at least one goal, each a goal of the charter (a legacy
    `G3` reads as `G-3`). Off while `charter` is unset; red when `charter` is set without
    `stories` (half set, as G-D12's pair), when the charter is missing or yields no goal rows,
    and on a charter goal id not in the standard form. With `task_goals` set, every open task names
    goals of the charter too (`task_goal_failures`), and `task_goals` without `charter` is red.

    Not checked: whether a story really serves the goal it names (judgement, at intake), the
    charter's own prose (its `Stories` column included), and retired stories (history)."""
    g = e.store.config.guards
    if g.task_goals and not g.charter:  # half set: open tasks would go unchecked under a clean lint
        return [Failure("G-I1", CONFIG_NAME, "[guards] task_goals is set but `charter` is not, so no task's goals are checked", "set [guards] charter to the charter, or unset task_goals")]
    if g.charter and not g.stories:  # half set: the guard would be off under a clean lint
        return [Failure("G-I1", CONFIG_NAME, "[guards] charter is set but `stories` is not, so no story is checked against the charter", "set [guards] stories to the kind holding the stories, or unset charter to switch G-I1 off")] + known_goals(e)[1]
    if not (g.charter and g.stories):
        return []
    known, out = known_goals(e)
    if not known:
        return out
    out += task_goal_failures(e, known)
    served: set[str | None] = set()
    for rid, rel, doc in _stories(e):
        if doc.get("story_status") == "retired":
            continue
        for p in goal_problems(doc.get("goals"), known):
            out.append(Failure("G-I1", rel, f"{rid} {p}", f"a story's goals are set at `record new` and never rewritten: if the charter lacks the goal, ask the owner (it may be a new goal, FRAMEWORK §6.2 step 2); if the story names the wrong one, record it again with the right goals and the owner's words as they are (`record new story`), then retire this one: {retire_hint(rid)}"))
        served |= {goal_id(v) for v in D.as_list(doc.get("goals"))}
    for gid in sorted(known - served, key=lambda x: int(x[2:])):
        out.append(Failure("G-I1", g.charter, f"goal {gid} is served by no story", f"record the owner's story for it (`record new story ... --set goals=[{gid}]`), or ask the owner whether the goal still stands (FRAMEWORK §3.1)"))
    return out


def task_goal_failures(e: Engine, known: set[str]) -> list[Failure]:
    """G-I1 on the board (CE-99, DEC-64): every open item of the `[guards] task_goals` kind names
    at least one goal in `goals`, each a goal of the charter, in the standard id form (a task's
    goals are set by `task set`, so no legacy form is kept). Off while `task_goals` is unset.

    Not checked: closed items (history, filed before tasks carried goals), whether an item really
    serves the goal it names (judgement: the rerank, procedures § Rerank), and other board kinds
    (an owner question serves whatever it blocks)."""
    name = e.store.config.guards.task_goals
    if not name:
        return []
    st = e.store
    kind = st.config.kind(name)
    out = []
    for path in st._files(kind):
        rid = st._id_of(kind, path)
        try:
            doc = st.read(path)
        except Exception:
            continue  # the schema check reports an unreadable record
        if rid is None or doc.get("state") != "open":
            continue
        for p in goal_problems(doc.get("goals"), known, legacy=False):
            out.append(Failure("G-I1", st._rel(path), f"{rid} {p}", f"name the charter goals it serves: `context-engine task set {rid} --set goals=[G-n, ...]`; an item serving no goal is a rerank's to flag for SOMEDAY or retirement (procedures § Rerank), and a goal the charter lacks is an owner question (FRAMEWORK §3.1)"))
    return out


LAST_RERANK_RE = re.compile(r"^Last rerank:[ \t]*(\S*)[ \t]*$", re.M)  # the charter's line (CE-99, DEC-68): quoted by orient's rerank due, never a trigger


def last_rerank(text: str) -> str | None:
    """The value of the charter's `Last rerank:` line (a session key, or `never`); None when the
    charter has no such line. The first line wins (a second one is the rerank's to tidy)."""
    m = LAST_RERANK_RE.search(text.replace("\r\n", "\n"))
    return m.group(1) if m else None


def retire_hint(rid: str) -> str:
    """The command that retires a story in favour of its replacement story, a new record with the same
    words (G-I1's and G-I2's remedies)."""
    return f"`record retire {rid} --by agent --superseded-by <new id> --why \"<what was wrong>\"`"


def logged_retires(e: Engine) -> dict[str, dict]:
    """The newest logged `record retire` of each story, by id (the line that set its
    `story_status`; the successor's `supersedes` line is not one)."""
    out: dict[str, dict] = {}
    for _, op in _ops(e):
        if isinstance(op, dict) and op.get("op") == "retire" and "story_status" in (op.get("fields") or ()):
            out[str(op.get("id"))] = op
    return out


def logged_confirms(e: Engine) -> dict[str, dict]:
    """The newest logged `record confirm` of each story, by id."""
    out: dict[str, dict] = {}
    for _, op in _ops(e):
        if isinstance(op, dict) and op.get("op") == "confirm" and "story_status" in (op.get("fields") or ()):
            out[str(op.get("id"))] = op
    return out


def confirm_problems(e: Engine, stories: list[tuple[str, str, object]]) -> list[tuple[str, str, str, str]]:
    """G-I2 on confirmations, as (id, path, message, remedy): a story that is not retired, whose
    actor is an agent's reconstruction and whose status is `live` or `unspecified`, was confirmed by
    `record confirm` (a logged `confirm` line), so whose words confirmed it are recorded; and a
    story that a logged `confirm` confirmed is not `unconfirmed` again. Retired stories are history."""
    done = logged_confirms(e)
    out = []
    for rid, rel, doc in stories:
        status = str(doc.get("story_status") or "")
        op = done.get(rid)
        if status in CONFIRMED and op is None and AGENT_ACTOR_RE.fullmatch(str(doc.get("actor") or "")):
            out.append((rid, rel, f"is `{status}` with an agent's actor, but no `record confirm` of it is logged, so nothing records who confirmed the reconstruction or in what words",
                        f"if the owner confirmed it, record their words: `record confirm {rid} --by owner --file <their words>` (add `--status unspecified` if it has no criterion yet); if not, restore `story_status: unconfirmed` from git (`git log -p` on the file)"))
        elif op is not None and status == "unconfirmed":
            out.append((rid, rel, f"was confirmed by `record confirm` in session {op.get('session')}, but its frontmatter now says `story_status: unconfirmed`",
                        f"a confirmation stands: restore `story_status` from git (`git log -p` on the file); if the owner withdrew the story, `record retire {rid} --by owner --why \"<their words>\"`"))
    return out


def retire_problems(e: Engine, stories: list[tuple[str, str, object]]) -> list[tuple[str, str, str, str]]:
    """G-I2 on retires, as (id, path, message, remedy): a retired story was retired by `record
    retire` (a logged `retire` line), so who retired it and why are recorded; a story that a logged
    `retire` retired is still `retired` and `status: deprecated` (a retirement is never undone); only
    a retired story is `status: deprecated` (FRAMEWORK §9.3's one mapping); and each id in a
    story's `superseded_by` or `supersedes` is a story, `superseded_by` only on a retired one."""
    done = logged_retires(e)
    known = {rid for rid, _, _ in stories}
    out = []
    for rid, rel, doc in stories:
        status = str(doc.get("story_status") or "")
        op = done.get(rid)
        if status == "retired" and op is None:
            out.append((rid, rel, "is `retired`, but no `record retire` of it is logged, so nothing records who retired it or why",
                        f"if it was retired, record who and why: `record retire {rid} --by owner --why \"<their words>\"` (or `--by agent --superseded-by <id>` when a replacement story replaces it); if it was not, restore `story_status` from git (`git log -p` on the file)"))
        elif op is not None and (status != "retired" or doc.get("status") != "deprecated"):
            now = f"`story_status: {status}`" if status != "retired" else f"`status: {doc.get('status') or ''}`, not `deprecated`"
            out.append((rid, rel, f"was retired by `record retire` in session {op.get('session')}, but its frontmatter now says {now}",
                        "a retirement is never undone: restore `story_status: retired` and `status: deprecated` from git (`git log -p` on the file); to bring the intent back, record it as a new story (`record new story`)"))
        elif op is None and status != "retired" and doc.get("status") == "deprecated":
            out.append((rid, rel, f"is `status: deprecated` but `{status}`: only a retired story is deprecated, so readers would skip it as history",
                        f"restore `status` from git; to retire {rid}, `record retire {rid}` (it writes both)"))
        for key in RETIRE_KEYS:
            for ref in D.as_list(doc.get(key)):
                if str(ref) not in known:
                    out.append((rid, rel, f"`{key}` names {ref}, which is not a story", "restore the link from git; story links are written only by `record retire`"))
        if D.as_list(doc.get("superseded_by")) and status != "retired":
            out.append((rid, rel, f"has `superseded_by` but is `{status}`, not retired", "restore the story from git; `record retire --superseded-by` writes the link and the retire together"))
    return out


def story_fields(e: Engine) -> list[Failure]:
    """G-I2: every story (`[guards] stories`) that is not retired has an actor from the
    vocabulary (`owner`, `human:<id>`, `agent (reconstructed from ...)`), a date and a
    `story_status` from the vocabulary, and `unconfirmed` only with an agent's actor
    (`story_problems`); every retired story was retired by `record retire`, and stays retired
    (`retire_problems`); every agent's reconstruction that is `live` or `unspecified` was confirmed by
    `record confirm`, and is not `unconfirmed` again (`confirm_problems`). Off while `stories` is unset.

    Not checked: whether the actor really spoke (git cannot tell, FRAMEWORK §3.2), `via`, a hand
    edit between `live` and `unspecified` (no operation owns that move, and the op log records which
    keys a write changed, not their values), an actor rewritten by hand (an agent's reconstruction
    made the owner's would pass), that a confirmation's amendment is still there, a retired
    story's frontmatter after the retirement (history), that the amendment a retirement wrote is still
    there, that `supersedes` mirrors `superseded_by`, and an op log line written by hand (it is
    trusted as written, as G-W7 trusts it)."""
    if not e.store.config.guards.stories:
        return []
    stories = _stories(e)

    def remedy(rid: str) -> str:
        return f"a story's provenance is set at `record new` and never rewritten: record the story again with the right actor, date and status and the owner's words as they are (`record new story`), then retire this one: {retire_hint(rid)}"

    out = [Failure("G-I2", rel, f"{rid}: {p}", remedy(rid)) for rid, rel, doc in stories for p in story_problems(doc)]
    out += [Failure("G-I2", rel, f"{rid} {msg}", rem) for rid, rel, msg, rem in retire_problems(e, stories)]
    return out + [Failure("G-I2", rel, f"{rid} {msg}", rem) for rid, rel, msg, rem in confirm_problems(e, stories)]


def _criteria(e: Engine, guard: str) -> tuple[list[Criterion], list[Failure]]:
    """The criterion rows of `[working] criteria`, and ``guard``'s failures when the file is missing,
    a table of criteria cannot be read, or it yields no rows (the table changed under the pattern)."""
    rel = e.w.criteria
    path = e.root / rel
    if not path.is_file():
        return [], [Failure(guard, CONFIG_NAME, f"[working] criteria names {rel}, which does not exist", "fix the path, or create the criteria file (FRAMEWORK §3.3)")]
    rows, problems = criteria_rows(_text(path))
    out = [Failure(guard, rel, p, remedy) for p, remedy in problems]
    if not rows and not problems:
        out.append(Failure(guard, rel, "no criterion rows: no table row starts with an id (`| AC-1 | ... |`), so nothing is traced", "write the criteria as table rows led by their ids, with `from` and `status` columns (FRAMEWORK §3.3)"))
    return rows, out


def _board_open(e: Engine) -> list[str]:
    """The text of every open board item (tasks and questions may share a directory)."""
    paths = sorted({p for k in e.w.board for p in e.store._files(e.store.config.kind(k))})
    return [t for t in (_text(p) for p in paths) if not _deprecated(t)]


def specified(e: Engine) -> list[Failure]:
    """G-T1: every `live` story is the source (`from`) of at least one criterion that is not
    retired; every `unspecified` story is named by an open board item (the task to specify it).
    Off while `stories` or `[working] criteria` is unset; red when the criteria file is missing or
    yields no rows.

    Not checked: whether the board item that names an `unspecified` story is the task to specify
    it or a passing mention (judgement; the session reads the item at intake), and stories in
    other statuses (`unconfirmed` waits on the owner, `retired` is history)."""
    if not (e.store.config.guards.stories and e.w.criteria):
        return []
    rows, out = _criteria(e, "G-T1")
    if not rows:
        return out  # no criterion could be read: one red for the file, not one per story
    sourced = {rid for r in rows if r.status != "retired" for rid in ID_RE.findall(r.source)}
    board: list[str] | None = None
    for rid, rel, doc in _stories(e):
        status = doc.get("story_status")
        if status == "live" and rid not in sourced:
            old = [str(s) for s in D.as_list(doc.get("supersedes")) if str(s) in sourced]
            remedy = (f"it replaced {', '.join(old)}: add {rid} to the `from` cell of the criteria that come from {', '.join(old)} in {e.w.criteria}, or draft its own"
                      if old else f"draft its criteria as `planned` rows of {e.w.criteria} with `from` {rid} (FRAMEWORK §6.2 step 3)")
            out.append(Failure("G-T1", rel, f"{rid} is live but no criterion comes from it", remedy))
        elif status == "unspecified":
            board = _board_open(e) if board is None else board
            if not any(re.search(rf"(?<![\w-]){re.escape(rid)}(?![\w-])", t) for t in board):
                out.append(Failure("G-T1", rel, f"{rid} is unspecified and no open board item names it", f"`task new` the work to specify {rid}; an owner question only if what the story means is unclear (FRAMEWORK §3.4)"))
    return out


def claims(e: Engine) -> list[Failure]:
    """G-T2: every `tested` or `manual` criterion is claimed by a test or driver (the `[guards]
    claim` pattern, in the files under `[guards] tests`), every claim names a criterion row, and
    every row's status is from the vocabulary. Off while `tests` is unset; red when it is set
    without `[working] criteria` (half set), a listed path is missing, the criteria file yields no rows, or the pattern
    finds no claim at all (it does not fit the repo's test syntax).

    Not checked: that a claiming test checks its criterion (a skipped test, an assert that cannot
    fail): the sabotage rule (P7) covers that by hand, mutation (G-T5) later; and tests that claim
    nothing (a test may be internal, FRAMEWORK §3.4)."""
    g = e.store.config.guards
    if g.tests and not e.w.criteria:  # half set: the guard would be off under a clean lint
        missing = [rel for rel in g.tests if not (e.root / rel).exists()]
        return [Failure("G-T2", CONFIG_NAME, "[guards] tests is set but [working] criteria is not, so no claim is traced", f"set [working] criteria to the criteria file, or {INTENT_OFF}")] + [Failure("G-T2", CONFIG_NAME, f"[guards] tests names {rel}, which does not exist", f"fix the path, or {INTENT_OFF}") for rel in missing]
    if not (g.tests and e.w.criteria):
        return []
    rows, out = _criteria(e, "G-T2")
    pattern = re.compile(g.claim)
    found: dict[str, tuple[str, int]] = {}
    for rel in g.tests:
        p = e.root / rel
        if not p.exists():
            out.append(Failure("G-T2", CONFIG_NAME, f"[guards] tests names {rel}, which does not exist", f"fix the path, or {INTENT_OFF}"))
            continue
        files = [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file() and f.suffix != ".pyc" and not SKIP_DIRS.intersection(f.relative_to(e.root).parts))
        for f in files:
            for n, line in enumerate(_text(f).split("\n"), 1):
                for m in pattern.finditer(line):
                    found.setdefault(m.group(1), (f.relative_to(e.root).as_posix(), n))
    if not found and not out:
        out.append(Failure("G-T2", CONFIG_NAME, f"[guards] claim matched nothing under {', '.join(g.tests)}, so no test is traced", "fit the pattern to the repo's test syntax (one group: the criterion id), or fix the paths"))
    ids = {r.id for r in rows}
    for r in rows:
        if r.status not in CRITERION_STATUSES:
            out.append(Failure("G-T2", e.w.criteria, f"line {r.line}: {r.id} has status `{r.status}`, none of {', '.join(CRITERION_STATUSES)}", "use a status from the vocabulary (FRAMEWORK §3.3)"))
        elif r.status in CLAIMED and found and r.id not in found:
            out.append(Failure("G-T2", e.w.criteria, f"line {r.line}: {r.id} is `{r.status}` but no test or driver claims it", "claim it in the test that checks it, once that test has been seen red with the behaviour broken (P7), or set the row back to `planned`"))
    for cid, (where, n) in sorted(found.items()):
        if rows and cid not in ids:
            out.append(Failure("G-T2", where, f"line {n}: claims {cid}, which is not a row of {e.w.criteria}", "claim an id that is a row, or add the row (ids are never reused, P3)"))
    return out


def sources(e: Engine) -> list[Failure]:
    """G-T6: every criterion's source cell (`from`) names at least one id, and each is a story
    (`[guards] stories`) or a decision (`[working] decision`). A criterion's actor is its
    source's, so resolving the source is the whole check. Off while `stories` or `[working]
    criteria` is unset; red when the criteria file is missing or yields no rows.

    Not checked: whether the criterion follows from its source (judgement, at intake), and text in
    the source cell that is not an id."""
    if not (e.store.config.guards.stories and e.w.criteria):
        return []
    rows, out = _criteria(e, "G-T6")
    st = e.store
    kinds = [st.config.kind(st.config.guards.stories)] + ([st.config.kind(e.w.decision)] if e.w.decision else [])
    known = {rid for k in kinds for p in st._files(k) if (rid := st._id_of(k, p))}
    names = " or ".join(f"{k.prefix}-n" for k in kinds)
    for r in rows:
        refs = ID_RE.findall(r.source)
        if not refs:
            out.append(Failure("G-T6", e.w.criteria, f"line {r.line}: {r.id} names no source (`{r.source}`)", f"name the story or decision it comes from ({names}) in its `from` cell"))
        for ref in refs:
            if ref not in known:
                out.append(Failure("G-T6", e.w.criteria, f"line {r.line}: {r.id} comes from {ref}, which is neither a story nor a decision", f"name a {names} that exists"))
    return out


def intent(e: Engine) -> list[Failure]:
    return goals(e) + story_fields(e) + specified(e) + claims(e) + sources(e)
