"""Decision records: the generated index, link fields, and the single-file log importer
(FRAMEWORK §6.5, §11.4; CE-5).

Everything here is a pure function of record frontmatter or of a log's text; the store and the
engine do the reading, the locking and the writing.

- The index (``render_index``) is built from frontmatter only, never from prose, so its check
  (G-D6) is byte equality with a regeneration.
- The importer (``plan_import``) reads a single-file log whose entries are headed
  ``### D-n -- title *(actor, date)*`` (``—`` and ``–`` also work), with an optional trailing
  ``-- **note**`` that may say ``SUPERSEDED by D-n``, ``relaxes D-n``, ``relaxed by D-n`` or
  ``narrowed by D-n``. Each entry keeps its text verbatim and its number; an id in another prefix
  is renamed to the kind's (``D-27`` becomes ``DEC-27``) and keeps its old id in ``aliases``
  (FRAMEWORK §11.4). The one table under a ``## `` heading that mentions "rejected", before the
  first entry, becomes one REJECTED record per row, with new ids above the highest imported one
  and no alias.
- The import never loses text silently (CE-98). An entry runs to the next entry heading (the
  last to the end of the log), keeping any ``#``/``## `` heading inside it, its own
  ``## Amendments`` among them, except for headings with no text of their own just before the
  next entry or the end (a log's date groups). Whatever is left out (before the first entry,
  bar the rejected table; those empty headings) is named by line in the import's output. A
  heading it cannot read refuses, naming every such line: a ``### `` heading that starts with an
  id but is not an entry (``### D-107 FIX``, ``### D-159b -- ...``, `` ### D-2 -- ...``,
  ``### **D-2** -- ...``) unless it stands under its own entry's ``## Amendments``; an
  attribution with no actor, or a date where the actor goes or inside it; a ``#``/``## ``
  heading after an entry's own ``## Amendments`` (its text would not be stamped); a
  ``## Amendments`` line in a fence or comment inside an entry (the stamp would end there); and
  a code fence or HTML comment never closed. Headings inside fences and HTML comments are text.

Deliberately not here: guessing a decision's status from its prose (an imported entry is BUILT
unless its heading note supersedes it, and the import says how many it defaulted so), and
reading a log in place without importing it (the §11.4 read adapter).
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any

from .errors import Refusal
from .okf import AMENDMENTS_HEADING

# Link fields a decision may carry (FRAMEWORK §6.5). Each is a list of ids, or of `file::symbol`
# for `code`. `superseded_by` and `narrowed_by` are backlinks the engine maintains.
LINK_FIELDS = ("supersedes", "superseded_by", "relaxes", "narrowed_by", "creates", "amends", "retires", "tasks", "code", "refs")
BACKLINK = {"supersedes": "superseded_by", "superseded_by": "supersedes", "relaxes": "narrowed_by", "narrowed_by": "relaxes"}
STATUS_KEY = "decision_status"
INDEX_TITLE = "# Decisions"
INDEX_NOTE = "Generated from each decision's frontmatter by `context-engine decision index`; never edit it by hand (G-D6)."
UNTAGGED = "untagged"


@dataclass
class Row:
    """One decision as the index sees it: frontmatter only."""

    id: str
    link: str  # the record's path relative to the index's directory
    data: dict[str, Any]

    @property
    def num(self) -> int:
        return int(self.id.rsplit("-", 1)[1])

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def tags(self) -> list[str]:
        return [str(t) for t in (self.get("tags") or [])]


def as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def index_line(r: Row) -> str:
    text = r.get("description") or r.get("title") or ""
    who = ", ".join(str(x) for x in (r.get("actor"), r.get("decided")) if x)
    line = f"- [{r.id}]({r.link}): {text}" + (f" *({who})*" if who else "")
    later = as_list(r.get("superseded_by"))
    if later:
        line += f"; superseded by {', '.join(later)}"
    return line


def render_index(rows: list[Row], statuses: tuple[str, ...]) -> str:
    """The index: grouped by status (in the kind's enum order, then any other value), then by
    each record's first tag (alphabetical, `untagged` last), one line per decision by id."""
    order = list(statuses) + sorted({str(r.get(STATUS_KEY)) for r in rows} - set(statuses))
    out = [INDEX_TITLE, "", INDEX_NOTE]
    for status in order:
        group = [r for r in rows if str(r.get(STATUS_KEY)) == status]
        if not group:
            continue
        out += ["", f"## {status}"]
        tags = sorted({(r.tags() or [UNTAGGED])[0] for r in group}, key=lambda t: (t == UNTAGGED, t))
        for tag in tags:
            out += ["", f"### {tag}", ""]
            out += [index_line(r) for r in sorted(group, key=lambda r: r.num) if (r.tags() or [UNTAGGED])[0] == tag]
    return "\n".join(out) + "\n"


# -- the single-file log importer -------------------------------------------------------------

DASH = r"(?:--|—|–)"
ID = r"[A-Za-z][A-Za-z0-9]*-\d+"
ENTRY_RE = re.compile(rf"^### (?P<id>{ID})[ \t]+{DASH}[ \t]+(?P<rest>.*?)[ \t]*$")
# a `###` heading (as CommonMark reads one) that starts like an entry but is not one: `### D-107 FIX`,
# `### D-159b -- ...`, ` ### D-2 -- ...`, `###  D-2 -- ...`, `### **D-2** -- ...`, `### [D-2] -- ...`
IDLIKE_RE = re.compile(rf"^ {{0,3}}###[ \t]+[*_\[`]*(?P<id>{ID})(?P<suffix>[A-Za-z0-9]*)\b")
# a heading at a level the importer does not read (`#`, `##`, `####` to `######`) shaped like an entry,
# an id then an attribution: `#### D-2 -- two *(owner, 2026-07-24)*` would fold into the entry above (CE-100)
SHAPED_RE = re.compile(rf"^ {{0,3}}(?P<hashes>#{{1,2}}|#{{4,6}})[ \t]+[*_\[`]*(?P<id>{ID})\b.*\*\(.*\)\*")
HEADING_TAIL = re.compile(rf"^(?P<title>.*?)[ \t]+\*\((?P<attr>.*?)\)\*(?:[ \t]+{DASH}[ \t]+(?P<note>.*))?$")
SECTION_RE = re.compile(r"^#{1,2} ")  # a `#` or `## ` heading: inside an entry it is kept
FENCE_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})")
COMMENT_RE = re.compile(r"^ {0,3}<!--")  # an HTML comment block (CommonMark type 2): it runs to the line holding `-->`
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
DATE_SHAPED = re.compile(r"^\d{4}-\d{2}-\d{2}\b")
UNRECORDED = "unrecorded"  # the actor of an entry whose log names no one (DEC-57): explicit, never guessed
UNRECORDED_HOW = f"`*({UNRECORDED}, <date>)*` when the log does not say who decided, never a guessed actor"
NOTE_LINKS = (
    (re.compile(r"\bsuperseded by\s+(?P<id>[A-Za-z]+-\d+)", re.I), "superseded_by"),
    (re.compile(r"\bsupersedes\s+(?P<id>[A-Za-z]+-\d+)", re.I), "supersedes"),
    (re.compile(r"\b(?:relaxed|narrowed) by\s+(?P<id>[A-Za-z]+-\d+)", re.I), "narrowed_by"),
    (re.compile(r"\b(?:relaxes|narrows)\s+(?P<id>[A-Za-z]+-\d+)", re.I), "relaxes"),
)
FIX_COPY = "fix it in the copy of the log, then import again"
EMPTY_HEADING = "a heading with no text of its own, outside every entry"


@dataclass
class Entry:
    """One record the importer will write."""

    id: str
    fields: dict[str, Any]
    body: str
    note: str = ""  # the heading's trailing note, kept as an amendment
    links: dict[str, list[str]] = field(default_factory=dict)
    old: str = ""  # the id in the log; for a rejected row, which row of which table
    line: int = 0  # the heading's line in the log


@dataclass
class Problem:
    """A heading the import cannot read: it refuses, naming every one (CE-98)."""

    line: int
    kind: str  # a short label, for the count by kind
    message: str
    remedy: str


@dataclass
class Excluded:
    """Lines of the log no entry holds, named in the import's output (CE-98)."""

    first: int
    last: int
    why: str
    head: str  # the range's first non-blank line

    def __str__(self) -> str:
        span = f"line {self.first}" if self.first == self.last else f"lines {self.first}-{self.last}"
        return f"{span} ({self.why}, from {self.head[:60]!r})"


@dataclass
class Table:
    """The rejected table: the first `## ` section before the first entry whose heading mentions
    "rejected" and that holds a table (outside fences and comments)."""

    heading: str  # without its `## `
    line: int  # the heading's line in the log
    at: int  # the table's header line in the log; its separator and rows follow it
    header: str
    sep: str
    rows: list[tuple[int, str]]  # (line in the log, the row verbatim)


@dataclass
class Parsed:
    entries: list[Entry]
    excluded: list[Excluded]
    rejected: Table | None
    inner: list[tuple[int, str, str]]  # every `#`/`## ` heading kept inside an entry: (line, entry id, heading)
    problems: list[Problem]


def _num(rid: str) -> int:
    return int(rid.rsplit("-", 1)[1])


@dataclass
class _Heads:
    kinds: dict[int, str]  # each heading line outside fences and comments, by index: `entry`, `idlike` or `section`
    hidden: set[int]  # every line inside a code fence or an HTML comment block, its opening and closing lines too
    fence: int | None  # the index of a fence never closed
    comment: int | None  # the index of an HTML comment never closed


def _headings(lines: list[str]) -> _Heads:
    """Each heading line outside code fences and HTML comment blocks, by index: `entry`,
    `idlike` (a `### ` heading that starts with an id but is not an entry) or `section` (`#`,
    `## `); which lines a fence or comment hides; and a fence or comment never closed."""
    out: dict[int, str] = {}
    hidden: set[int] = set()
    fence, opened, comment = "", None, None
    for i, ln in enumerate(lines):
        if fence:
            hidden.add(i)
            if re.match(rf"^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*$", ln):
                fence, opened = "", None
            continue
        if comment is not None:
            hidden.add(i)
            if "-->" in ln:
                comment = None
            continue
        f = FENCE_RE.match(ln)
        c = COMMENT_RE.match(ln)
        if f and not (f["fence"][0] == "`" and "`" in ln[f.end() :]):  # a backtick fence's info string has no backtick (CommonMark)
            fence, opened = f["fence"], i
            hidden.add(i)
        elif c and "-->" not in ln[c.end() :]:
            comment = i
            hidden.add(i)
        elif ENTRY_RE.match(ln):
            out[i] = "entry"
        elif IDLIKE_RE.match(ln):
            out[i] = "idlike"
        elif SECTION_RE.match(ln):
            out[i] = "section"
    return _Heads(out, hidden, opened, comment)


def _idlike(n: int, line: str) -> Problem:
    m = IDLIKE_RE.match(line)
    rid, show = m["id"], line[:80]
    if m["suffix"]:
        return Problem(
            n, "letter id", f"line {n}: {show!r} has the id {rid}{m['suffix']}, which has no number of its own",
            f"in the copy, move it under a `## Amendments` heading at the end of {rid}'s text, where it is kept as an amendment, or give it a free number as its own entry; then import again",
        )
    return Problem(
        n, "not an entry heading", f"line {n}: {show!r} starts with {rid} but is not an entry heading (`### <id> -- title *(actor, date)*`, from the line's start)",
        f"in the copy: if it amends {rid}, move it under a `## Amendments` heading at the end of {rid}'s text; if it is an entry, write its heading as one; if it is a sub-heading, make it `####`; then import again",
    )


def _shaped(n: int, line: str) -> Problem:
    m = SHAPED_RE.match(line)
    rid, level = m["id"], len(m["hashes"])
    return Problem(
        n, "entry heading at another level", f"line {n}: {line[:80]!r} is shaped like an entry heading for {rid} (an id, then `*(actor, date)*`), but at level {level}, and the import reads entries only at `### `",
        f"in the copy: if it is an entry, write its heading `### {rid} -- title *(actor, date)*`; if it is part of the entry above, reword the heading so it does not start with an id and an attribution; then import again",
    )


def _span(lines: list[str], a: int, b: int, why: str) -> Excluded | None:
    """The lines [a, b) as an exclusion (1-based, blank lines at either end left out), or None if blank."""
    full = [i for i in range(a, b) if lines[i].strip()]
    if not full:
        return None
    return Excluded(full[0] + 1, full[-1] + 1, why, lines[full[0]].strip())


def _spans(lines: list[str], a: int, b: int, why: str, held: set[int]) -> list[Excluded]:
    """The lines [a, b) that ``held`` leaves out, as exclusions, one per run between held lines."""
    out: list[Excluded] = []
    run = a
    for i in [*sorted(j for j in held if a <= j < b), b]:
        x = _span(lines, run, i, why)
        if x:
            out.append(x)
        run = i + 1
    return out


def _rejected(lines: list[str], h: _Heads, first: int, problems: list[Problem]) -> Table | None:
    """The rejected table (``Table``): only before the first entry, so a table inside an entry
    stays that entry's text; a second table in its section refuses, naming its line."""
    heads = sorted(i for i, k in h.kinds.items() if k == "section" and i < first)
    for k, i in enumerate(heads):
        if not lines[i].startswith("## ") or "rejected" not in lines[i].lower():
            continue
        end = heads[k + 1] if k + 1 < len(heads) else first
        table = [j for j in range(i + 1, end) if j not in h.hidden and lines[j].startswith("|")]
        if len(table) < 2:
            continue
        block = [table[0]]
        while block[-1] + 1 in table:
            block.append(block[-1] + 1)
        heading = lines[i][3:].strip()
        for j in table[len(block) :][:1]:
            problems.append(Problem(j + 1, "second rejected table", f"line {j + 1}: a second table under `## {heading}` (line {i + 1}), whose first table the import reads as rejected rows", "the import reads one table of rejected rows: merge the two in the copy, or move the second out of that section; then import again"))
        return Table(heading, i + 1, block[0] + 1, lines[block[0]], lines[block[1]], [(j + 1, lines[j]) for j in block[2:]])
    return None


def _entry(m: re.Match, n: int, body: str, problems: list[Problem]) -> Entry | None:
    rid, line = m["id"], m.string[:80]
    where = f"the heading of {rid} (line {n})"
    tail = HEADING_TAIL.match(m["rest"])
    if not tail:
        problems.append(Problem(n, "no attribution", f"{where} has no `*(actor, date)*` after its title: {line!r}", f"{FIX_COPY}; {UNRECORDED_HOW}"))
        return None
    attr = tail["attr"].strip()
    actor = attr.split(",")[0].split(";")[0].strip()
    found = DATE_RE.findall(attr)
    mine: list[Problem] = []
    if not actor:
        mine.append(Problem(n, "no actor", f"{where} names no actor", f"{FIX_COPY}; {UNRECORDED_HOW}"))
    elif DATE_SHAPED.match(actor):
        mine.append(Problem(n, "date as actor", f"{where} has a date where the actor goes: {attr!r}", f"name who decided before the date in the copy, `*(<actor>, <date>)*`; {UNRECORDED_HOW}; then import again"))
    elif DATE_RE.search(actor):
        mine.append(Problem(n, "date in actor", f"{where} has no comma between its actor and its date, so the actor would be {actor!r}", f"write it `*(<actor>, <date>)*` in the copy; {UNRECORDED_HOW}; then import again"))
    elif not found:
        mine.append(Problem(n, "no date", f"{where} has no YYYY-MM-DD date", f"add the date to the copy of the log (from git history if the log has none; `*({UNRECORDED}, <date>)*` if it names no one either), then import again"))
    else:
        try:
            decided = dt.date.fromisoformat(found[-1])
        except ValueError:
            mine.append(Problem(n, "bad date", f"{where} has a date {found[-1]!r} that is not a real day", FIX_COPY))
    if not AMENDMENTS_HEADING.split(body, 1)[0].strip():
        mine.append(Problem(n, "no text", f"{rid} (line {n}) has no text under its heading", "an entry is imported with its words; add them in the copy, or drop the entry"))
    problems += mine
    if mine:
        return None
    fields: dict[str, Any] = {"title": tail["title"].strip(), "actor": actor, "decided": decided}
    if attr != f"{actor}, {decided.isoformat()}":
        fields["attribution"] = attr  # it says more than actor and date: keep all of it
    note = (tail["note"] or "").strip()
    links: dict[str, list[str]] = {}
    for rx, key in NOTE_LINKS:
        for hit in rx.finditer(note):
            links.setdefault(key, []).append(hit["id"])
    return Entry(rid, fields, body + "\n", note, links, line=n)


def parse_log(text: str) -> Parsed:
    """Read a single-file log: every `### <id> -- title *(actor, date)*` entry in file order with
    its text verbatim, the rejected table, what neither holds (named by line), and every line it
    cannot read. Pure: it refuses nothing itself (``parse_entries`` and ``plan_import`` do)."""
    lines = text.replace("\r\n", "\n").split("\n")
    h = _headings(lines)
    heads = h.kinds
    problems: list[Problem] = []
    if h.fence is not None:
        problems.append(Problem(h.fence + 1, "unclosed fence", f"line {h.fence + 1}: a code fence {lines[h.fence].strip()[:20]!r} is never closed, so every heading after it would be read as code", "close the fence in the copy of the log, then import again"))
    if h.comment is not None:
        problems.append(Problem(h.comment + 1, "unclosed comment", f"line {h.comment + 1}: an HTML comment {lines[h.comment].strip()[:20]!r} is never closed (`-->`), so every heading after it would be read as a comment", "close the comment in the copy of the log, then import again"))
    starts = [i for i in sorted(heads) if heads[i] == "entry"]
    first = starts[0] if starts else len(lines)
    inner: list[tuple[int, str, str]] = []
    entries: list[Entry] = []
    table = _rejected(lines, h, first, problems)
    held = {table.line - 1, *range(table.at - 1, table.at + 1 + len(table.rows))} if table else set()  # the rejected table's lines become records
    excluded = _spans(lines, 0, first, "before the first entry", held)
    stray = {i for i, k in heads.items() if k == "idlike"}  # each refuses, unless under its own entry's `## Amendments`
    for k, at in enumerate(starts):
        m = ENTRY_RE.match(lines[at])
        rid = m["id"]
        start, end = at + 1, starts[k + 1] if k + 1 < len(starts) else len(lines)
        # headings with no text of their own just before the next entry (or the end) are the log's, not this entry's
        stop, j, empty = end, end - 1, []
        while j >= start and (not lines[j].strip() or heads.get(j) == "section"):
            if lines[j].strip():
                stop = j
                empty.append(Excluded(j + 1, j + 1, EMPTY_HEADING, lines[j].strip()))
            j -= 1
        excluded.extend(reversed(empty))
        amends = None  # the line of this entry's own `## Amendments`
        for i in range(start, end):
            if i >= stop:
                if amends is None and heads.get(i) == "section" and AMENDMENTS_HEADING.match(lines[i]):
                    amends = i
            elif heads.get(i) == "section":
                inner.append((i + 1, rid, lines[i].strip()))
                if amends is not None:
                    problems.append(Problem(
                        i + 1, "heading after amendments", f"line {i + 1}: {lines[i].strip()[:80]!r} comes after {rid}'s own `## Amendments` (line {amends + 1}), so its text would be imported as an amendment, not stamped",
                        f"in the copy: move {rid}'s own text above its `## Amendments` heading, or make the heading `###` or deeper if it is part of an amendment; then import again",
                    ))
                elif AMENDMENTS_HEADING.match(lines[i]):
                    amends = i
            elif heads.get(i) == "idlike" and amends is not None and IDLIKE_RE.match(lines[i])["id"] == rid:
                stray.discard(i)  # `### D-107 FIX` under D-107's own `## Amendments`: part of its amendments (DEC-57)
            elif i in h.hidden and AMENDMENTS_HEADING.match(lines[i]):
                problems.append(Problem(
                    i + 1, "amendments heading in a fence", f"line {i + 1}: a `## Amendments` line inside a code fence or comment in {rid}: the record keeps it as text, but its stamp would end there",
                    "in the copy, indent that line by one space (or reword it), then import again",
                ))
        if k + 1 < len(starts) and amends is not None and ENTRY_RE.match(lines[end])["id"] == rid:
            problems.append(Problem(
                end + 1, "amendment as entry", f"line {end + 1}: {lines[end][:80]!r} is an entry heading for {rid} under {rid}'s own `## Amendments` (line {amends + 1})",
                f"an amendment heading is not an entry: in the copy, write it `### {rid} <label>` with no dash or attribution (`### {rid} FIX`), then import again",
            ))
        e = _entry(m, at + 1, "\n".join(lines[start:stop]).strip("\n"), problems)
        if e:
            entries.append(e)
    problems += [_idlike(i + 1, lines[i]) for i in stray]
    problems += [_shaped(i + 1, ln) for i, ln in enumerate(lines) if i not in h.hidden and SHAPED_RE.match(ln)]
    problems.sort(key=lambda p: p.line)
    excluded.sort(key=lambda x: x.first)
    return Parsed(entries, excluded, table, inner, problems)


def refusal(problems: list[Problem]) -> Refusal:
    """One refusal for every line the import cannot read: the first in full, then how many of
    each kind and on which lines, so a copy can be fixed in one pass."""
    p = problems[0]
    if len(problems) == 1:
        return Refusal(p.message, p.remedy)
    kinds: dict[str, list[int]] = {}
    for q in problems:
        kinds.setdefault(q.kind, []).append(q.line)
    each = "; ".join(f"{k} x{len(v)} (line{'s' if len(v) > 1 else ''} {', '.join(map(str, v[:8]))}{', ...' if len(v) > 8 else ''})" for k, v in kinds.items())
    return Refusal(f"{p.message}; {len(problems)} lines in all that the import cannot read: {each}", p.remedy)


def parse_entries(text: str) -> list[Entry]:
    """Every `### <id> -- title *(actor, date)*` entry, in file order, with its text verbatim;
    refused if any heading cannot be read (``parse_log``)."""
    parsed = parse_log(text)
    if parsed.problems:
        raise refusal(parsed.problems)
    return parsed.entries


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


IMPORT_LATER = (
    "for entries added to the log since it was imported, import a copy holding only them (and no rejected "
    "table); record one whose number is taken with `record new decision ... --set aliases=[<old id>]` (it "
    "gets the next free number, and the old id still resolves)"
)
REJECTED_LABEL = "(rejected table row {n})"


def plan_import(
    text: str, prefix: str, used: set[int], source: str, aliases: dict[str, list[str]] | None = None, rejected: dict[str, str] | None = None
) -> tuple[list[Entry], list[str], Parsed]:
    """Every record an import of ``text`` writes, ids decided, links in both directions; what
    it noted (what no entry holds among it, by line); and the parsed log, for ``layout``. An id in another prefix is renamed to ``prefix`` with its number kept, and
    the old id goes into `aliases` (FRAMEWORK §11.4); ``aliases`` is the store's alias map, and
    ``rejected`` maps the title of each REJECTED decision already imported to its id.
    Refuses before anything is written: two entries with one id (before or after the rename), an
    id in the kind's own prefix not written as the engine writes it (`DEC-01`), a number already
    in use, an old id that is already a record's alias, a rejected row already imported, a
    heading that does not parse (all of them named at once), a link to an id not in the log."""
    parsed = parse_log(text)
    if parsed.problems:
        raise refusal(parsed.problems)
    entries = parsed.entries
    if not entries:
        raise Refusal("the log has no `### <id> -- title *(actor, date)*` entries", "point the import at a single-file decision log")
    aliases = aliases or {}
    for e in entries:
        e.old, e.id = e.id, f"{prefix}-{_num(e.id)}"
        if e.old != e.id and e.old.rsplit("-", 1)[0] == prefix:
            raise Refusal(f"the log's entry {e.old} is in the kind's own prefix but not written as the engine writes it", f"write it {e.id} in the copy (no leading zeros), then import again")
    olds = [e.old for e in entries]
    dup = sorted({i for i in olds if olds.count(i) > 1})
    if dup:
        raise Refusal(f"the log has two entries {dup[0]}", "give one of them its own id in the copy, then import again")
    ids = [e.id for e in entries]
    clash = next((e.id for e in entries if ids.count(e.id) > 1), None)
    if clash:
        group = [e.old for e in entries if e.id == clash]
        raise Refusal(f"the log's entries {', '.join(group)} would all become {clash}", "the import keeps each number: give one of them its own number in the copy, then import again")
    for e in entries:
        owners = aliases.get(e.old, [])
        if owners and all(re.fullmatch(rf"{re.escape(prefix)}-\d+", o) for o in owners):
            raise Refusal(f"{e.old} was imported already: it is an alias of {', '.join(owners)}", IMPORT_LATER)
        if owners:
            raise Refusal(f"{e.old} is already an alias of {', '.join(owners)}", "an alias names one record: drop it from that record (`task set <id> --set aliases=[...]`), or rename the entry in the copy")
        if _num(e.id) in used:
            what = f"{e.old} would become {e.id}, which" if e.old != e.id else e.id
            raise Refusal(f"{what} is already a record in the decisions directory", f"the import writes into a free series: run it once, before any decision is recorded there; {IMPORT_LATER}")
    by_old = {e.old: e for e in entries}
    for e in entries:
        e.fields["imported_from"] = source
        if e.old != e.id:
            e.fields["aliases"] = [e.old]
        for key, targets in e.links.items():
            for t in targets:
                if t not in by_old:
                    raise Refusal(f"the heading note of {e.old} links {t}, which is not in the log", "fix the note in the copy of the log, then import again")
                back = by_old[t].links.setdefault(BACKLINK[key], [])
                if e.old not in back:
                    back.append(e.old)
    for e in entries:
        for key in list(e.links):
            e.links[key] = sorted(dict.fromkeys(by_old[t].id for t in e.links[key]), key=_num)
        e.fields["decision_status"] = "SUPERSEDED" if e.links.get("superseded_by") else "BUILT"
    rows: list[tuple[str, str, list[str]]] = []  # per row: header, separator and row verbatim; its first cell; the rest
    table = parsed.rejected  # only before the first entry: a table inside an entry is that entry's text
    heading = table.heading if table else ""
    for n, (ln, row) in enumerate(table.rows if table else [], 1):
        cells, width = _cells(row), len(_cells(table.header))
        if len(cells) != width:
            raise Refusal(f"row {n} of the table under `## {heading}` (line {ln}) has {len(cells)} cells, the header {width}", "escape a `|` inside a cell as `\\|` in the copy, then import again")
        rows.append((f"{table.header}\n{table.sep}\n{row}\n", cells[0], cells[1:]))
    nxt = max({_num(i) for i in ids} | used) + 1
    by_new = {e.id: e for e in entries}
    before = rejected or {}
    rejected = []
    for n, (block, what, rest) in enumerate(rows, 1):
        if what in before:
            raise Refusal(f"the rejected row {what[:60]!r} was imported already, as {before[what]}", f"drop the `## {heading}` table from the copy; {IMPORT_LATER}")
        cited = dict.fromkeys(re.findall(r"\b[A-Za-z][A-Za-z0-9]*-\d+\b", rest[-1] if rest else ""))
        refs = list(dict.fromkeys((by_old.get(i) or by_new[i]).id for i in cited if i in by_old or i in by_new))
        when = DATE_RE.findall(" ".join(rest[:-1]))
        first = next((e for e in entries if refs and e.id == refs[0]), None)
        decided = dt.date.fromisoformat(when[-1]) if when else (first.fields["decided"] if first else None)
        if decided is None:
            raise Refusal(f"the rejected row {what[:60]!r} has no date and names no entry", "add `(YYYY-MM-DD)` to its verdict in the copy, then import again")
        fields: dict[str, Any] = {
            "title": what,
            "actor": "agent",
            "decided": decided,
            "decision_status": "REJECTED",
            "attribution": f"a row of the `{heading}` table" + (f"; the reasoning is under {', '.join(refs)}" if refs else ""),
            "imported_from": source,
        }
        rid = f"{prefix}-{nxt}"
        nxt += 1
        rejected.append(Entry(rid, fields, f"Imported from the table under `## {heading}`:\n\n{block}", "", {"refs": refs} if refs else {}, REJECTED_LABEL.format(n=n)))
    span = sorted(entries, key=lambda e: _num(e.id))
    renamed = [e for e in entries if e.old != e.id]
    if renamed:
        notes = [f"{len(entries)} entries ({span[0].old}..{span[-1].old} as {span[0].id}..{span[-1].id}, numbers kept, {len(renamed)} old ids kept as aliases)"]
    else:
        notes = [f"{len(entries)} entries ({span[0].id}..{span[-1].id}, ids kept)"]
    if rejected:
        notes.append(f"{len(rejected)} rejected rows as {rejected[0].id}..{rejected[-1].id}")
    noted = [e.id for e in entries if e.note]
    if noted:
        notes.append(f"{len(noted)} heading notes kept as amendments")
    unrecorded = [e for e in entries if e.fields["actor"] == UNRECORDED]
    if unrecorded:
        notes.append(f"{len(unrecorded)} with actor `{UNRECORDED}`, as the log names no one")
    own = [e for e in entries if AMENDMENTS_HEADING.search(e.body)]
    if own:
        notes.append(f"{len(own)} entries' own `## Amendments` kept as their records' amendments (not stamped)")
    if parsed.inner:
        notes.append(f"{len(parsed.inner)} `#`/`## ` headings kept inside {len({i for _, i, _ in parsed.inner})} entries")
    if parsed.excluded:
        notes.append("not imported: " + excluded_line(parsed.excluded))
    built = [e for e in entries if e.fields["decision_status"] == "BUILT"]
    if built:
        notes.append(f"{len(built)} set BUILT by default, as the log gives no status: review each and `decision set <id> --set decision_status=<status>` any that was parked, deferred or not built")
    return entries + rejected, notes, parsed


def excluded_line(excluded: list[Excluded]) -> str:
    """What no record holds, on one line: each range by its lines, the headings with no text of
    their own (a log's date groups) by count and line."""
    empty = [x.first for x in excluded if x.why == EMPTY_HEADING]
    out = [str(x) for x in excluded if x.why != EMPTY_HEADING]
    if empty:
        out.append(f"{len(empty)} heading{'s' if len(empty) > 1 else ''} with no text of {'their' if len(empty) > 1 else 'its'} own (line{'s' if len(empty) > 1 else ''} {', '.join(map(str, empty))})")
    return ", ".join(out)


def layout(parsed: Parsed) -> str:
    """For the dry run's evidence doc: every range no entry holds, and every `#`/`## ` heading
    kept inside an entry, by line, so a reader can check each was placed as meant."""
    out = ["## Not imported", ""]
    out += [f"- line{'s' if x.last > x.first else ''} {x.first}{f'-{x.last}' if x.last > x.first else ''}: {x.why}: {x.head[:80]!r}" for x in parsed.excluded] or ["- nothing: every line is in an entry"]
    out += ["", "## Headings kept inside entries", ""]
    out += [f"- line {n}, in {rid}: {h[:80]!r}" for n, rid, h in parsed.inner] or ["- none"]
    return "\n".join(out) + "\n"


def id_map(planned: list[Entry]) -> str:
    """The import's id map as a markdown table, one row per record: the id in the log (or which
    table row), the new id, the status and the title. Save it as an evidence doc (FRAMEWORK §11.4)."""
    def cell(t: Any) -> str:
        return str(t).replace("|", "\\|")

    out = ["| id in the log | record | status | title |", "|---|---|---|---|"]
    out += [f"| {cell(e.old)} | {e.id} | {e.fields['decision_status']} | {cell(e.fields['title'])} |" for e in planned]
    return "\n".join(out) + "\n"


