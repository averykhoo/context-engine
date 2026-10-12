"""Decision records: the generated index, link fields, and the single-file log importer
(FRAMEWORK §6.5, §11.4; CE-5).

Everything here is a pure function of record frontmatter or of a log's text; the store and the
engine do the reading, the locking and the writing.

- The index (``render_index``) is built from frontmatter only, never from prose, so its check
  (G-D6) is byte equality with a regeneration.
- The importer (``plan_import``) reads a single-file log whose entries are headed
  ``### D-n -- title *(actor, date)*`` (``—`` and ``–`` also work), with an optional trailing
  ``-- **note**`` that may say ``SUPERSEDED by D-n``, ``relaxes D-n``, ``relaxed by D-n`` or
  ``narrowed by D-n``. Each entry keeps its id and its text verbatim. A table under a ``## ``
  heading that mentions "rejected" becomes one REJECTED record per row, with new ids.

Deliberately not here: guessing a decision's status from its prose (an imported entry is BUILT
unless its heading note supersedes it), and reading a log in place without importing it (the
§11.4 read adapter).
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any

from .errors import Refusal

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
ENTRY_RE = re.compile(rf"^### (?P<id>[A-Za-z][A-Za-z0-9]*-\d+)[ \t]+{DASH}[ \t]+(?P<rest>.*?)[ \t]*$", re.MULTILINE)
HEADING_TAIL = re.compile(rf"^(?P<title>.*?)[ \t]+\*\((?P<attr>.*?)\)\*(?:[ \t]+{DASH}[ \t]+(?P<note>.*))?$")
STOP_RE = re.compile(r"^#{1,2} ", re.MULTILINE)  # a `#` or `## ` heading ends an entry
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
NOTE_LINKS = (
    (re.compile(r"\bsuperseded by\s+(?P<id>[A-Za-z]+-\d+)", re.I), "superseded_by"),
    (re.compile(r"\bsupersedes\s+(?P<id>[A-Za-z]+-\d+)", re.I), "supersedes"),
    (re.compile(r"\b(?:relaxed|narrowed) by\s+(?P<id>[A-Za-z]+-\d+)", re.I), "narrowed_by"),
    (re.compile(r"\b(?:relaxes|narrows)\s+(?P<id>[A-Za-z]+-\d+)", re.I), "relaxes"),
)


@dataclass
class Entry:
    """One record the importer will write."""

    id: str
    fields: dict[str, Any]
    body: str
    note: str = ""  # the heading's trailing note, kept as an amendment
    links: dict[str, list[str]] = field(default_factory=dict)


def _date(text: str, where: str) -> dt.date:
    found = DATE_RE.findall(text)
    if not found:
        raise Refusal(f"{where} has no YYYY-MM-DD date", "add the date to the copy of the log, then import again")
    try:
        return dt.date.fromisoformat(found[-1])
    except ValueError:
        raise Refusal(f"{where} has a date {found[-1]!r} that is not a real day", "fix it in the copy of the log") from None


def parse_entries(text: str) -> list[Entry]:
    """Every `### <id> -- title *(actor, date)*` entry, in file order, with its text verbatim."""
    text = text.replace("\r\n", "\n")
    heads = list(ENTRY_RE.finditer(text))
    out: list[Entry] = []
    for n, m in enumerate(heads):
        start = m.end() + 1
        end = heads[n + 1].start() if n + 1 < len(heads) else len(text)
        stop = STOP_RE.search(text, start, end)
        body = text[start : stop.start() if stop else end].strip("\n")
        rid = m["id"]
        line = text[m.start() : m.end()]
        tail = HEADING_TAIL.match(m["rest"])
        if not tail:
            raise Refusal(f"the heading of {rid} has no `*(actor, date)*` after its title: {line[:80]!r}", "fix the heading in the copy of the log, then import again")
        attr = tail["attr"].strip()
        actor = attr.split(",")[0].split(";")[0].strip()
        if not actor:
            raise Refusal(f"the heading of {rid} names no actor", "fix the heading in the copy of the log")
        decided = _date(attr, f"the heading of {rid}")
        if not body.strip():
            raise Refusal(f"{rid} has no text under its heading", "an entry is imported with its words; add them in the copy, or drop the entry")
        fields: dict[str, Any] = {"title": tail["title"].strip(), "actor": actor, "decided": decided}
        if attr != f"{actor}, {decided.isoformat()}":
            fields["attribution"] = attr  # it says more than actor and date: keep all of it
        note = (tail["note"] or "").strip()
        links: dict[str, list[str]] = {}
        for rx, key in NOTE_LINKS:
            for hit in rx.finditer(note):
                links.setdefault(key, []).append(hit["id"])
        out.append(Entry(rid, fields, body + "\n", note, links))
    return out


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_rejected(text: str) -> tuple[str, list[tuple[str, str, list[str]]]]:
    """The first `## ` section whose heading mentions "rejected" that holds a table: its heading,
    and per row (the header line plus separator plus the row, verbatim; the row's first cell;
    every cell's text after the first)."""
    text = text.replace("\r\n", "\n")
    parts = re.split(r"^## (.*)$", text, flags=re.MULTILINE)
    for i in range(1, len(parts), 2):
        heading, section = parts[i].strip(), parts[i + 1]
        if "rejected" not in heading.lower():
            continue
        lines = [ln for ln in section.splitlines() if ln.startswith("|")]
        if len(lines) < 2:
            continue
        header, sep, rows = lines[0], lines[1], lines[2:]
        width = len(_cells(header))
        out = []
        for n, row in enumerate(rows, 1):
            cells = _cells(row)
            if len(cells) != width:
                raise Refusal(f"row {n} of the table under `## {heading}` has {len(cells)} cells, the header {width}", "escape a `|` inside a cell as `\\|` in the copy, then import again")
            out.append((f"{header}\n{sep}\n{row}\n", cells[0], cells[1:]))
        return heading, out
    return "", []


def plan_import(text: str, prefix: str, used: set[int], source: str) -> tuple[list[Entry], list[str]]:
    """Every record an import of ``text`` writes, ids decided, links in both directions; and
    what it noted. Refuses before anything is written: a foreign prefix, a duplicate id, an id
    already in use, a heading that does not parse, a link to an id not in the log."""
    entries = parse_entries(text)
    if not entries:
        raise Refusal("the log has no `### <id> -- title *(actor, date)*` entries", "point the import at a single-file decision log")
    ids = [e.id for e in entries]
    foreign = sorted({i.rsplit("-", 1)[0] for i in ids} - {prefix})
    if foreign:
        raise Refusal(f"the log's ids use the prefix {foreign[0]!r}, but the decision kind's is {prefix!r}", f"set `prefix = \"{foreign[0]}\"` in [kinds.decision] of context.toml: an existing series keeps its ids (FRAMEWORK §11.4)")
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise Refusal(f"the log has two entries {dup[0]}", "give one of them its own id in the copy, then import again")
    nums = {int(i.rsplit("-", 1)[1]) for i in ids}
    taken = sorted(nums & used)
    if taken:
        raise Refusal(f"{prefix}-{taken[0]} is already a record in the decisions directory", "the import writes into an empty series: run it once, before any decision is recorded there")
    by_id = {e.id: e for e in entries}
    for e in entries:
        e.fields["imported_from"] = source
        for key, targets in e.links.items():
            for t in targets:
                if t not in by_id:
                    raise Refusal(f"the heading note of {e.id} links {t}, which is not in the log", "fix the note in the copy of the log, then import again")
                back = by_id[t].links.setdefault(BACKLINK[key], [])
                if e.id not in back:
                    back.append(e.id)
    for e in entries:
        for key in list(e.links):
            e.links[key] = sorted(dict.fromkeys(e.links[key]), key=lambda i: int(i.rsplit("-", 1)[1]))
        e.fields["decision_status"] = "SUPERSEDED" if e.links.get("superseded_by") else "BUILT"
    heading, rows = parse_rejected(text)
    nxt = max(nums | used) + 1
    rejected = []
    for block, what, rest in rows:
        refs = [i for i in re.findall(rf"\b{re.escape(prefix)}-\d+\b", rest[-1] if rest else "") if i in by_id]
        when = DATE_RE.findall(" ".join(rest[:-1]))
        decided = dt.date.fromisoformat(when[-1]) if when else (by_id[refs[0]].fields["decided"] if refs else None)
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
        rejected.append(Entry(rid, fields, f"Imported from the table under `## {heading}`:\n\n{block}", "", {"refs": refs} if refs else {}))
    span = sorted(entries, key=lambda e: int(e.id.rsplit("-", 1)[1]))
    notes = [f"{len(entries)} entries ({span[0].id}..{span[-1].id}, ids kept)"]
    if rejected:
        notes.append(f"{len(rejected)} rejected rows as {rejected[0].id}..{rejected[-1].id}")
    noted = [e.id for e in entries if e.note]
    if noted:
        notes.append(f"{len(noted)} heading notes kept as amendments")
    return entries + rejected, notes
