"""Freezing and archiving docs (FRAMEWORK §6.7, §7.2, §7.3, CE-27): the text each write makes.

``doc freeze`` puts a FROZEN line with the date above a doc's liveness declaration (G-D4's
reading, ``guards.declared``), so the topmost declaration, the one G-D4 counts, is FROZEN and the
old one stays below it as history. ``doc archive`` moves a whole doc into an archive directory
unrepaired, opening it with ``ARCHIVED <date>``, and adds a row to that directory's one redirect
table, its ``README.md``. The Engine methods (``working.Engine.doc_freeze``,
``working.Engine.doc_archive``) check the caller, take the lock and log the writes; this module
only computes text, keeping every byte of the doc it does not add.

Deliberately not here: pruning part of a file into an archive under a dated heading (§7.3's
``## Pruned from HANDOFF.md on <date>``), which needs a judgement of what to prune; it is done by
hand (manual-mode.md § context-engine doc archive).
"""

from __future__ import annotations

import re
import textwrap
from urllib.parse import quote

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


def archived(text: str, date: str, session: str, was: str) -> str:
    """``text`` opened with its ARCHIVED line (FRAMEWORK §7.3: the first line), then a blank line;
    nothing else in it changes."""
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    body = text[len(bom):]
    nl = _ending(_lines(body)[0])
    return f"{bom}ARCHIVED {date} (session {session}), from {was}.{nl}{nl}{body}"


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
            "LIVING: the redirect table of this archive directory, one row per archived doc, added by\n"
            "`context-engine doc archive` (FRAMEWORK §7.3). Nothing else here is repaired, extended or\n"
            "kept current.\n\n"
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
