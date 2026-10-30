"""Freezing and archiving docs (FRAMEWORK §6.7, §7.2, §7.3): the text each write makes.

``doc freeze`` puts a FROZEN line with the date above a doc's liveness declaration (G-D4's
reading, ``guards.declared``), so the topmost declaration, the one G-D4 counts, is FROZEN and the
old one stays below it as history. ``doc archive`` moves a whole doc into an archive directory
unrepaired, opening it with ``ARCHIVED <date>`` (first after its frontmatter, whose `liveness:`
key, if it has one, becomes FROZEN), and adds a row to that directory's one redirect table, its
``README.md``; material that is not markdown moves byte for byte. ``doc archive --lines`` prunes
a passage instead: cut from the doc and appended unchanged to the directory's
``<stem>-pruned.md`` under ``## Pruned from <doc> on <date>`` (§7.3's index headings). The
Engine methods (``working.Engine.doc_freeze``, ``working.Engine.doc_archive``) check the caller,
take the lock and log the writes; this module only computes text, keeping every byte of the doc
it does not add.

Deliberately not here: which passage to prune, a judgement the caller makes by naming its lines.
"""

from __future__ import annotations

import re
import textwrap
from urllib.parse import quote

from . import guards as G

REDIRECTS = "README.md"  # each archive directory's one redirect table (FRAMEWORK §7.3, §10)
REDIRECT_HEAD = "| Was | Now | Archived | Why |"
REDIRECT_RULE = "|---|---|---|---|"
# JUDGEMENT: the prose wrap of this repo's runbooks, so a long note never trips a route's G-D1
# `max_width`; wrong if a repo's caps are narrower
WRAP = 100


def _lines(body: str) -> list[str]:
    """``body`` split after each `\\n`, every line keeping its own ending (the last may be empty)."""
    return re.split(r"(?<=\n)", body)


def _ending(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def frozen_line(date: str, session: str, note: str) -> str:
    """The FROZEN line: the date, the session that froze the doc, and why."""
    return f"FROZEN {date} (session {session}): {' '.join(note.split())}"


def freeze(text: str, line: int, stamp: str) -> str:
    """``text`` with ``stamp`` (wrapped at ``WRAP``) and a blank line inserted above its line
    ``line``, counted from 1 after any BOM, as ``guards.declared`` counts. The stamp opens a block
    where the declaration did (after a blank line, a heading, the frontmatter, or at the top), and
    the declaration, now after a blank line, still opens one: the topmost, FROZEN, counts."""
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    lines = _lines(text[len(bom):])
    at = line - 1
    nl = _ending(lines[at]) if lines[at].endswith("\n") else _ending(lines[at - 1]) if at else "\n"
    block = nl.join(textwrap.wrap(stamp, WRAP, break_long_words=False, break_on_hyphens=False)) + nl + nl
    return bom + "".join(lines[:at]) + block + "".join(lines[at:])


def frontmatter(text: str) -> int | None:
    """The index of the line closing the frontmatter that opens ``text`` (after any BOM), or None
    when it has none: G-D4's reading (``guards.frontmatter_end``), so a thematic break is not one."""
    return G.frontmatter_end(text.lstrip("\ufeff").replace("\r\n", "\n").split("\n"))


def thawed_keys(text: str) -> list[int]:
    """The lines (indexes, after any BOM) of the `liveness:` keys in ``text``'s frontmatter that
    are not FROZEN: G-D4 reads such a key before any line below the frontmatter."""
    end = frontmatter(text)
    flat = text.lstrip("\ufeff").replace("\r\n", "\n").split("\n")
    return [i for i in range(1, end or 0) if (m := G.FM_LIVENESS_RE.match(flat[i])) and m.group(1) != "FROZEN"]


def archived(text: str, date: str, session: str, was: str) -> str:
    """``text`` opened with its ARCHIVED line (FRAMEWORK §7.3: the first line), then a blank line.
    A doc with frontmatter keeps it on top and takes the ARCHIVED line first after it, where G-D4
    reads it too; a `liveness:` key there, which G-D4 reads before any line below, becomes FROZEN,
    keeping its old value in a comment (DEC-122). Nothing else in it changes."""
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    body = text[len(bom):]
    lines = _lines(body)
    nl = _ending(lines[0])
    stamp = f"ARCHIVED {date} (session {session}), from {was}."
    end = frontmatter(text)
    if end is None:
        return f"{bom}{stamp}{nl}{nl}{body}"
    head = lines[: end + 1]
    for i in thawed_keys(text):
        flat = head[i].rstrip("\r\n")
        head[i] = f"liveness: FROZEN  # ARCHIVED {date}; was {flat[len('liveness:'):].strip()}" + head[i][len(flat):]
    if not head[end].endswith("\n"):  # the frontmatter is the whole file, with no final newline
        head[end] += nl
    return bom + "".join(head) + f"{stamp}{nl}{nl}" + "".join(lines[end + 1:])


def line_count(text: str) -> int:
    """How many lines ``text`` has, as an editor numbers them (a final newline opens none)."""
    lines = _lines(text.lstrip("\ufeff"))
    return len(lines) - (lines[-1] == "")


def cut(text: str, first: int, last: int) -> tuple[str, str]:
    """``text`` without its lines ``first`` to ``last`` (counted from 1 after any BOM), and those
    lines, each with its own line ending: (what stays, the passage)."""
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    lines = _lines(text[len(bom):])
    return bom + "".join(lines[: first - 1] + lines[last:]), "".join(lines[first - 1: last])


def pruned_heading(was: str, date: str) -> str:
    """The heading a pruned passage goes under: the archive file's index (FRAMEWORK §7.3)."""
    return f"## Pruned from {was} on {date}"


def pruned(old: str | None, passage: str, was: str, date: str, session: str) -> str:
    """The archive file with ``passage`` appended unchanged under its dated heading. With no file
    yet, a new one, opened with its ARCHIVED line; an existing one keeps every byte it has, and
    gains a final newline if it had none."""
    nl = _ending(_lines(old.lstrip("\ufeff"))[0]) if old else _ending(_lines(passage)[0])
    if not passage.endswith("\n"):
        passage += nl
    if old is None:
        top = f"ARCHIVED {date} (session {session}), passages pruned from {was}, each under its dated heading.{nl}"
    else:
        top = old if not old or old.endswith("\n") else old + nl
    return f"{top}{nl}{pruned_heading(was, date)}{nl}{nl}{passage}"


def _cell(text: str) -> str:
    return " ".join(text.replace("|", "\\|").split())


def redirect_row(was: str, name: str, date: str, session: str, why: str) -> str:
    """One row of the redirect table: the old path, a link to the archived doc, when, and why."""
    return f"| {_cell(was)} | [{_cell(name)}]({quote(name)}) | {date} (session {session}) | {_cell(why) or '—'} |"


def redirects(old: str | None, directory: str, row: str) -> str:
    """The archive directory's redirect table with ``row`` added: after the last row of the
    table under ``REDIRECT_HEAD``, or, in a README that has no such table (written by hand), in a
    new section at its end. With no README, a new one, LIVING: its rows are kept current, while
    nothing else in an archive is."""
    if old is None:
        return (
            f"# Archive: {directory}\n\n"
            "LIVING: the redirect table of this archive directory, one row per archived doc or pruned\n"
            "passage, added by `context-engine doc archive` (FRAMEWORK §7.3). Nothing else here is\n"
            "repaired, extended or kept current.\n\n"
            f"{REDIRECT_HEAD}\n{REDIRECT_RULE}\n{row}\n"
        )
    bom = "\ufeff" if old.startswith("\ufeff") else ""
    lines = _lines(old[len(bom):])
    head = next((i for i, ln in enumerate(lines) if ln.strip() == REDIRECT_HEAD), None)
    if head is not None:
        end = head + 1
        while end < len(lines) and lines[end].lstrip().startswith("|"):
            end += 1
        nl = _ending(lines[end - 1])
        if not lines[end - 1].endswith("\n"):  # the table is the file's last line, with no newline
            lines[end - 1] += nl
        return bom + "".join(lines[:end]) + row + nl + "".join(lines[end:])
    nl = _ending(lines[0])
    body = "".join(lines)
    if body and not body.endswith("\n"):
        body += nl
    return f"{bom}{body}{nl}## Redirects{nl}{nl}{REDIRECT_HEAD}{nl}{REDIRECT_RULE}{nl}{row}{nl}"
