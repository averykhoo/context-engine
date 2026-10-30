"""The criterion write op's text work (CE-42, FRAMEWORK §3.3, §6.2 step 3): find a criteria table
or a criterion's row in the criteria file, and write one row, appended or rewritten in place, so
that every other byte of the file stays as it was (a hand-edited markdown table is never
reflowed). Criteria stay rows of `[working] criteria`, not a record kind (DEC-33). The tables are
read by guards.py's one parser (``guards.table_blocks``); the checks a write makes are the guards'
own (``Engine.criterion_new``, ``Engine.criterion_set``).

Deliberately not here: the lock, the op log and the refusals that need the repo (working.py).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import guards as G
from .errors import Refusal

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")  # an ATX heading: `## Core (CE-1)`
PREFIX = "AC"  # the criterion series when the file has no row yet (the kit's criteria.md says ids are `AC-n`)
CLAIMED_BY = "claimed by"  # the kit table's column naming the claiming test: filled when a row becomes `tested` or `manual`
LISTED = 6  # headings a refusal lists as examples; JUDGEMENT: enough to recognise the file's sections in one line
TEXT_COLUMNS = ("criterion", "text", "scenario")  # the column a criterion's words go in, by its header; else the second column


@dataclass(frozen=True)
class Place:
    """A criteria table, and the heading it sits under ('' above the first heading)."""

    table: G.Table
    heading: str

    @property
    def columns(self) -> tuple[int, int, int]:
        """(source, status, text) column indexes. Only a criteria table is a ``Place``, so the
        first two are never None."""
        src, status = G.criteria_columns(self.table.header)
        text = next((self.table.header.index(c) for c in TEXT_COLUMNS if c in self.table.header), 1)
        return src, status, text  # type: ignore[return-value]


def lines(raw: str) -> list[str]:
    """The file's lines, each with its own line ending (none on a last line without one). Split
    on LF only, as the guards read it, so line n here is line n of ``guards.prose``."""
    return [ln for ln in re.split(r"(?<=\n)", raw) if ln]


def _flat(raw: str) -> str:
    return raw.replace("\r\n", "\n")


def headings(text: str) -> list[tuple[int, int, str]]:
    """(line number, level, title) of each ATX heading outside fenced code."""
    out = []
    for n, line in G.prose(text):
        m = HEADING_RE.match(line)
        if m:
            out.append((n, len(m.group(1)), m.group(2).strip()))
    return out


def places(raw: str) -> list[Place]:
    """Every criteria table in the file (a table whose header has a `status` column and a source
    column, `from`, `story` or `source`, as G-T2 and G-T6 read them), with rows or without, each
    with the nearest heading above it."""
    text = _flat(raw)
    heads = headings(text)
    out = []
    for t in G.table_blocks(text):
        src, status = G.criteria_columns(t.header)
        if src is None or status is None:
            continue
        above = [title for n, _, title in heads if n < t.head]
        out.append(Place(t, above[-1] if above else ""))
    return out


def target(raw: str, under: str) -> Place:
    """The criteria table a new row goes in, among those whose first column is headed `id`: with
    ``under``, the first in the section of the heading whose title is ``under`` (up to the next
    heading of the same or a higher level); without it, the file's only one, and a refusal listing
    headings when there are several (where a criterion goes is a choice, never a default)."""
    text = _flat(raw)
    found = [p for p in places(raw) if p.table.header[0] == "id"]  # a row the op writes is one criteria_rows reads as its id
    write_by_hand = "write the heading and the table's header row and `|---|` line by hand (manual-mode.md § context-engine criterion new), then run it again"
    if not under.strip():
        if not found:
            raise Refusal("the criteria file has no criteria table (a table whose first column is `id` and whose header has `status` and `from`, `story` or `source` columns)", write_by_hand)
        if len(found) > 1:
            titles = list(dict.fromkeys(p.heading for p in found if p.heading))
            shown = ", ".join(f"`{t}`" for t in titles[-LISTED:]) + (f" (and {len(titles) - LISTED} more)" if len(titles) > LISTED else "")
            raise Refusal(f"the criteria file has {len(found)} criteria tables, so where the row goes is a choice", f"name the heading of the table it belongs under with --under, e.g. {shown}")
        return found[0]
    heads = headings(text)
    named = [(n, level) for n, level, title in heads if title == under.strip()]
    if not named:
        raise Refusal(f"the criteria file has no heading `{under.strip()}`", f"name a heading the file has (the text after the `#`s), or {write_by_hand}")
    if len(named) > 1:
        raise Refusal(f"the criteria file has {len(named)} headings `{under.strip()}` (lines {', '.join(str(n) for n, _ in named)})", "give one of them a title of its own by hand, then name it")
    n, level = named[0]
    end = next((m for m, lv, _ in heads if m > n and lv <= level), None)
    inside = [p for p in found if p.table.head > n and (end is None or p.table.head < end)]
    if not inside:
        raise Refusal(f"the section `{under.strip()}` holds no criteria table", write_by_hand)
    return inside[0]


def rows_of(raw: str, cid: str) -> list[tuple[Place, int, list[str]]]:
    """(place, line number, cells) of each row of a criteria table whose first cell is ``cid``."""
    return [(p, n, cells) for p in places(raw) for n, cells in p.table.body if cells and cells[0] == cid]


def cell_problem(value: str, what: str) -> str | None:
    """Why ``value`` cannot be one table cell as written, or None: a line break would end the row,
    and a `|` that is not escaped (`\\|`), or a trailing backslash, would move the cell boundaries."""
    if "\n" in value or "\r" in value:
        return f"the {what} holds a line break, which would end the row"
    if len(G.PIPE_RE.split(value)) > 1:
        return f"the {what} holds a `|`, which would split the cell"
    if value.endswith("\\"):
        return f"the {what} ends in a backslash, which would escape the cell's closing `|`"
    return None


def _eol(line: str, raw: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return "\r\n" if "\r\n" in raw else "\n"


def append(raw: str, place: Place, cells: list[str]) -> str:
    """``raw`` with one row, `| c1 | c2 | ... |`, right after the table's last line, in that line's
    line ending. Nothing else changes, except that a file whose last line is the table's and has
    no line ending gets one before the new row (which then has none, as the file had)."""
    ls = lines(raw)
    i = place.table.last - 1
    row = "| " + " | ".join(cells) + " |"
    last = ls[i]
    if last.endswith("\n"):
        ls.insert(i + 1, row + _eol(last, raw))
    else:
        ls[i] = last + _eol(last, raw)
        ls.insert(i + 1, row)
    return "".join(ls)


def rewrite(raw: str, line: int, changes: dict[int, str]) -> str:
    """``raw`` with the cells ``changes`` names (column index -> new value) of row ``line``
    rewritten as ` value `; every other cell keeps its bytes, the row keeps its line ending, and
    every other line is unchanged."""
    ls = lines(raw)
    old = ls[line - 1]
    end = len(old) - len(old.rstrip("\r\n"))
    body, eol = old[: len(old) - end], old[len(old) - end:]
    pipes = [m.start() for m in G.PIPE_RE.finditer(body)]
    closed = body.rstrip().endswith("|") and not body.rstrip().endswith("\\|")
    spans = [(pipes[k] + 1, pipes[k + 1]) for k in range(len(pipes) - 1)]
    if not closed:
        spans.append((pipes[-1] + 1, len(body.rstrip())))
    for col in sorted(changes, reverse=True):
        if col >= len(spans):
            raise Refusal(f"line {line} has {len(spans)} cells, fewer than its table's header", "give the row a cell for every column by hand, then run it again")
        a, b = spans[col]
        body = body[:a] + f" {changes[col]}" + (" " if closed or col < len(spans) - 1 else "") + body[b:]
    ls[line - 1] = body + eol
    return "".join(ls)
