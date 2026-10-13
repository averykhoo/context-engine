"""The guard catalogue's doc, trace and tool-ownership guards (FRAMEWORK §8.2 to §8.4; CE-14).

Each guard is one function from an :class:`~context_engine.working.Engine` to a list of
:class:`~context_engine.store.Failure`, and each docstring says what it deliberately does not
check (P7). ``lint`` runs them all; ``Engine.lint`` drops the ids ``[guards] off`` names.

What a doc guard reads is configured, never guessed: G-D1's caps sit on ``[[routes]]``, and G-D3,
G-T3 and G-D7 read the paths listed in ``[guards]``. A path list that is empty checks nothing.
G-D12 reads the spec and the coverage maps ``[guards]`` names, and is off while neither is set.
G-T3 also reads the `code:` links of the ``[working] decision`` kind's current records.

Not here (FRAMEWORK §8, with their homes): G-D4 liveness and G-D5 typed numbers, G-T5 mutation
per criterion, G-T4 structural anchors, G-T7 deviations, G-W9 to G-W11 (housekeeping), G-V1 to
G-V3 (the run ledger), and the intent chain (G-I1, G-I2, G-T1, G-T2, G-T6).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Iterator

from . import decisions as D
from . import ledger as L
from .config import CONFIG_NAME
from .store import Failure, key_order

if TYPE_CHECKING:
    from .working import Engine

FENCE_RE = re.compile(r"^\s*(```|~~~)")
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
SKIP_DIRS = {".git", ".scratch", ".context", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache"}


def lint(e: Engine) -> list[Failure]:
    return caps(e) + ids(e) + links(e) + signals(e) + note_layers(e) + provenance(e) + existence(e) + tool_owned(e) + coverage(e)


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


def prose(text: str, history: bool = False) -> Iterator[tuple[int, str]]:
    """(line number, line) outside fenced code and frontmatter, with inline code kept. With
    ``history``, blockquotes and lines carrying a ``*HISTORY —*`` note are skipped too."""
    lines = text.split("\n")
    i = 0
    if lines and lines[0] == "---":
        end = next((j for j in range(1, len(lines)) if lines[j] == "---"), None)
        if end is not None:
            i = end + 1
    fence = False
    for n in range(i, len(lines)):
        line = lines[n]
        if FENCE_RE.match(line):
            fence = not fence
            continue
        if fence:
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
        if self._by_name is None:
            self._by_name = {}
            for d, dirs, files in os.walk(self.root):
                dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.endswith(".egg-info")]
                for f in files:
                    self._by_name.setdefault(f, []).append((Path(d) / f).relative_to(self.root).as_posix())
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
            raw = path.read_bytes()
            text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
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


# -- G-D2 ids ----------------------------------------------------------------------------


def ids(e: Engine) -> list[Failure]:
    """G-D2 at rest: no two files of a series carry the same id (by file name or by `id:`), and
    the op log never shows an id created twice (a reuse).

    Not checked: an id reused before the op log began, or after a record was deleted outside the
    engine with no op logged (allocation already scans closed records and never reuses, AC-4)."""
    out: list[Failure] = []
    st = e.store
    for kind in st.config.kinds.values():
        seen: dict[str, list[str]] = {}
        for path in st._files(kind):
            names = {st._id_of(kind, path)}
            try:
                fid = st.read(path).get("id")
            except Exception:
                fid = None  # the schema check reports an unreadable record
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
    `file::symbol` resolves to any file of that name in the repo; a symbol resolves when each of
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


# -- G-T3 existence in normative text ----------------------------------------------------


def existence(e: Engine) -> list[Failure]:
    """G-T3: in each doc `[guards] existence` lists (criteria, a law doc, the invariants
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


# -- G-D7 signal budgets -----------------------------------------------------------------


def signals(e: Engine) -> list[Failure]:
    """G-D7: in each doc `[guards] signals` lists, at most `warn_max` ⚠ and `bold_caps_max` bold
    all-caps spans (`**NEVER**`: a bold span with a run of four capitals and no lower case), and
    no glyph from `retired_glyphs`. A signal ranks only while it is rare.

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


# -- G-D8 the note's layer detector ------------------------------------------------------


def note_layers(e: Engine) -> list[Failure]:
    """G-D8: the orientation note has at most one `## Banner (<key>)` heading (G-W1 asks for
    one), no other heading carries a session key (a session's section, or a ledger entry heading
    pasted in), and no bullet or bold lead in the banner is a session key (a session's layer).

    Not checked: session keys inside a sentence (dated facts cite them as provenance), the
    banner's size (G-D1 on the note's route), and an inline board's position: the board is one
    file per item, read with `task list`."""
    rel = e.w.handoff
    path = e.root / rel if rel else None
    if path is None or not path.is_file():
        return []
    text = _text(path)
    out: list[Failure] = []
    banners = L.BANNER_RE.findall(text)
    if len(banners) > 1:
        out.append(Failure("G-D8", rel, f"{len(banners)} banner headings ({', '.join(banners)})", "keep the newest; `banner set` replaces the banner, it never adds one"))
    key_head = re.compile(rf"^#+ .*\b{KEY_RE}\b")
    layered = [line for _, line in prose(text) if key_head.match(line) and not L.BANNER_RE.match(line)]
    if layered:
        out.append(Failure("G-D8", rel, f"{len(layered)} headings carry a session key (the first: {layered[0].strip()!r}): session history in the note", "move it to the ledger, or into the one banner; the note is replaced, not layered"))
    b = L.find_banner(text)
    if b is not None:
        lead = re.compile(rf"^\s*(?:(?:[-*+]|\d+\.)\s+\**|\*\*)\s*{KEY_RE}\b")  # a bullet or bold lead, not a wrapped line
        layers = [ln for ln in b.text.split("\n") if lead.match(ln)]
        if layers:
            out.append(Failure("G-D8", rel, f"{len(layers)} banner lines start with a session key (the first: {layers[0].strip()[:60]!r}): a layered banner", "rewrite the banner as what is true now, under its one key; history goes in the ledger"))
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
    """G-W7 at rest: every session-keyed tool-owned key of a board item (`moved`, `updated`,
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


# -- G-D12 framework coverage ------------------------------------------------------------

# What G-D12 extracts from the spec, each class with its floor: fewer than the floor means the
# spec's format changed under the pattern, so the class is red rather than silently unchecked.
# Floors: provenance: JUDGEMENT, CE-30; FRAMEWORK.md held 23 components, 14 rituals and 41 G-ids
# on 2026-10-13a (counted by these patterns); wrong if the spec is trimmed below them on purpose.
COMPONENT_SECTION_RE = re.compile(r"^##\s+2\.\s")  # §2 "The components at a glance": its table
COMPONENT_RE = re.compile(r"^\|\s*\d+\s*\|[^|]*\|\s*\*\*(?P<name>[^*|]+?)\*\*")  # `| 1 | Intent | **Charter** |`
RITUAL_RE = re.compile(r"^###\s+(?P<num>5\.6|6\.\d+)\s+(?P<name>.+?)\s*$")  # `### 6.1 Session start`
GID_RE = re.compile(r"(?<![\w-])G-[A-Z]\d+(?!\w)")  # `G-D3`
COVERAGE_FLOORS = {"component": 20, "ritual": 10, "G-id": 30}
MAP_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})([a-z]*)")
# Where a coverage map's table owns each class: (a header that marks the table, the header of the
# column holding the key). A component row's `§` cell is not a ritual, nor is a guard row's.
MAP_COLUMNS = {"component": ("Component", "Component"), "ritual": ("Ritual", "§"), "G-id": ("Guard", "Guard")}


@dataclass(frozen=True)
class Owned:
    """One thing the spec names that something must own: its class, its key, and how to name it."""

    cls: str
    key: str  # a component's name, `§6.4`, or `G-D3`
    label: str

    def in_cell(self, cell: str) -> bool:
        """A map row names it: the cell is the key (a component's cell may add a parenthesis)."""
        return cell == self.key or (self.cls == "component" and cell.startswith(self.key + " ("))

    def in_text(self, text: str) -> bool:
        """A board item names it: the key as a word (`§6.1` is not `§6.13`; `G-D1` is not `G-D10`)."""
        return re.search(rf"(?<![\w-]){re.escape(self.key)}(?!\w|\.\d)", text) is not None


def spec_items(text: str) -> dict[str, list[Owned]]:
    """Every component (§2's table), ritual (§5.6 and §6.n headings) and G-id the spec names, by
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
        m = RITUAL_RE.match(line)
        if m:
            add(Owned("ritual", f"§{m['num']}", f"ritual §{m['num']} {m['name']!r}"))
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
    whose header row has the class's marking header, the cells under its key column
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
        for cls, (mark, column) in MAP_COLUMNS.items():
            if mark in header and column in header and header.index(column) < len(cells):
                out[cls].add(cells[header.index(column)])
    return out


def coverage(e: Engine) -> list[Failure]:
    """G-D12: every component (§2's table), ritual (§5.6, §6.n headings) and G-id the spec
    (`[guards] coverage_spec`) names is owned: a table row of the newest coverage map
    (`[guards] coverage_maps`, a repo-relative glob; newest by the date and session letters in
    the file name) names it in its class's key column (`MAP_COLUMNS`: `Component`; `§` in a
    table with a `Ritual` column; `Guard`), or a board item, open or closed, names it. Red when
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
        out.append(Failure("G-D12", p.relative_to(e.root).as_posix(), "matches [guards] coverage_maps but has no date (YYYY-MM-DD) in its name, so the newest map cannot be told", "rename it with its date, or narrow the coverage_maps glob"))
    if not maps and not undated:
        out.append(Failure("G-D12", CONFIG_NAME, f"[guards] coverage_maps matches no file ({g.coverage_maps})", f"fix the glob, {off}"))
    if out:
        return out
    items = spec_items(_text(spec))
    for cls, floor in COVERAGE_FLOORS.items():
        if len(items[cls]) < floor:
            out.append(Failure("G-D12", g.coverage_spec, f"{len(items[cls])} {cls}s extracted, under the floor of {floor}: the spec's format no longer matches the pattern, so they would go unchecked", "the patterns and floors are the engine's (guards.py: COMPONENT_RE, RITUAL_RE, GID_RE, COVERAGE_FLOORS) and fit FRAMEWORK.md's format: change them in the engine with a provenance note if FRAMEWORK changed on purpose; a repo whose spec they do not fit switches G-D12 off (`[guards] off = [\"G-D12\"]`, or unset both coverage_spec and coverage_maps)"))
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
