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
  (FRAMEWORK §11.4). A table under a ``## `` heading that mentions "rejected" becomes one REJECTED
  record per row, with new ids above the highest imported one and no alias.

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
    old: str = ""  # the id in the log; for a rejected row, which row of which table


def _num(rid: str) -> int:
    return int(rid.rsplit("-", 1)[1])


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


IMPORT_LATER = (
    "for entries added to the log since it was imported, import a copy holding only them (and no rejected "
    "table); record one whose number is taken with `record new decision ... --set aliases=[<old id>]` (it "
    "gets the next free number, and the old id still resolves)"
)
REJECTED_LABEL = "(rejected table row {n})"


def plan_import(
    text: str, prefix: str, used: set[int], source: str, aliases: dict[str, list[str]] | None = None, rejected: dict[str, str] | None = None
) -> tuple[list[Entry], list[str]]:
    """Every record an import of ``text`` writes, ids decided, links in both directions; and
    what it noted. An id in another prefix is renamed to ``prefix`` with its number kept, and
    the old id goes into `aliases` (FRAMEWORK §11.4); ``aliases`` is the store's alias map, and
    ``rejected`` maps the title of each REJECTED decision already imported to its id.
    Refuses before anything is written: two entries with one id (before or after the rename), an
    id in the kind's own prefix not written as the engine writes it (`DEC-01`), a number already
    in use, an old id that is already a record's alias, a rejected row already imported, a
    heading that does not parse, a link to an id not in the log."""
    entries = parse_entries(text)
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
    heading, rows = parse_rejected(text)
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
    built = [e for e in entries if e.fields["decision_status"] == "BUILT"]
    if built:
        notes.append(f"{len(built)} set BUILT by default, as the log gives no status: review each and `decision set <id> --set decision_status=<status>` any that was parked, deferred or not built")
    return entries + rejected, notes


def id_map(planned: list[Entry]) -> str:
    """The import's id map as a markdown table, one row per record: the id in the log (or which
    table row), the new id, the status and the title. Save it as an evidence doc (FRAMEWORK §11.4)."""
    def cell(t: Any) -> str:
        return str(t).replace("|", "\\|")

    out = ["| id in the log | record | status | title |", "|---|---|---|---|"]
    out += [f"| {cell(e.old)} | {e.id} | {e.fields['decision_status']} | {cell(e.fields['title'])} |" for e in planned]
    return "\n".join(out) + "\n"


