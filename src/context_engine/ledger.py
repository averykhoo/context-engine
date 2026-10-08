"""The session ledger and the banner: the two working-state files that are not records.

The ledger is one markdown file, newest entry first, each entry headed
``## <key> · kind: <kind>`` and separated by a ``---`` line (FRAMEWORK §7.1). It stays one file
under the engine lock rather than one file per entry (Q-H, DEC-14): every existing reader cites
the single file, and the lock already serialises writers.

The banner is the ``## Banner (<key>)`` section of the orientation note (FRAMEWORK §5.1). It is
prose; the engine only stamps its key and guards its write with a hash (§5.5 rule 2).

Deliberately not handled: rotating the ledger by period (FRAMEWORK §7.1), and entries written
in any other heading shape (they are not entries to this parser, and lint reports none of them).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import re
import textwrap
from dataclasses import dataclass

from .errors import Refusal
from .store import SESSION_RE, key_order

ENTRY_RE = re.compile(r"^## (?P<key>\d{4}-\d{2}-\d{2}[a-z]+) · kind: (?P<kind>[a-z]+)[ \t]*$", re.MULTILINE)
SEPARATOR_RE = re.compile(r"\n---[ \t]*\n\s*\Z")
BANNER_RE = re.compile(r"^## Banner \((?P<key>\d{4}-\d{2}-\d{2}[a-z]+)\)[ \t]*$", re.MULTILINE)
KINDS = ("open", "close", "pause", "foreign", "abandoned")
WIDTH = 100
EMPTY_LEDGER = "# Session ledger\n\nAppend-only, newest first, one entry per session (FRAMEWORK §7.1).\n\n---\n\n"


# -- session keys -------------------------------------------------------------------------


def _letters_to_int(s: str) -> int:
    n = 0
    for c in s:
        n = n * 26 + (ord(c) - 96)
    return n


def _int_to_letters(n: int) -> str:
    out = ""
    while n:
        n, r = divmod(n - 1, 26)
        out = chr(97 + r) + out
    return out


def next_key(newest: str | None, today: dt.date) -> str:
    """``max(newest, today's first key) + 1 letter``: a later day restarts at ``a``; the same day,
    or a clock behind the newest key, takes the next letter (z is followed by aa)."""
    day = today.isoformat()
    if newest is None or newest[:10] < day:
        return day + "a"
    return newest[:10] + _int_to_letters(_letters_to_int(newest[10:]) + 1)


def newest(keys) -> str | None:
    keys = [k for k in keys if k]
    return max(keys, key=key_order) if keys else None


# -- ledger -------------------------------------------------------------------------------


@dataclass
class Entry:
    key: str
    kind: str
    text: str  # heading to end of entry, without the trailing separator; ends in "\n"

    def field(self, name: str) -> str | None:
        """The text of a ``- **name:**`` bullet, continuation lines joined."""
        m = re.search(rf"^- \*\*{re.escape(name)}(?::\*\*| \*\*|\*\*:?)(.*(?:\n  .*)*)", self.text, re.MULTILINE)
        return " ".join(part.strip() for part in m.group(1).splitlines()).strip() if m else None

    def receipt(self, name: str) -> str | None:
        """The text of a ``  - name: ...`` line under ``- **receipts:**``."""
        m = re.search(rf"^  - {re.escape(name)}:(.*(?:\n    .*)*)", self.text, re.MULTILINE)
        return " ".join(part.strip() for part in m.group(1).splitlines()).strip() if m else None


@dataclass
class Ledger:
    preamble: str
    entries: list[Entry]
    newline: str = "\n"

    def render(self) -> str:
        pre = self.preamble
        if self.entries and not re.search(r"(^|\n)---[ \t]*\n\s*$", pre):
            pre = pre.rstrip("\n") + "\n\n---\n\n"
        blocks = [e.text.rstrip("\n") + "\n" for e in self.entries]
        text = pre + "\n---\n\n".join(blocks)
        return text.replace("\n", self.newline) if self.newline != "\n" else text

    def keys(self) -> list[str]:
        return [e.key for e in self.entries]

    def get(self, key: str) -> Entry | None:
        return next((e for e in self.entries if e.key == key), None)

    def after(self, key: str, kinds=("close", "pause")) -> list[Entry]:
        """Entries of the given kinds keyed after ``key``."""
        return [e for e in self.entries if e.kind in kinds and key_order(e.key) > key_order(key)]


def parse_ledger(text: str) -> Ledger:
    newline = "\r\n" if text.count("\r\n") * 2 > text.count("\n") else "\n"
    text = text.replace("\r\n", "\n")
    heads = list(ENTRY_RE.finditer(text))
    if not heads:
        return Ledger(text, [], newline)
    entries = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        block = SEPARATOR_RE.sub("\n", text[m.start() : end])
        entries.append(Entry(m.group("key"), m.group("kind"), block.rstrip("\n") + "\n"))
    return Ledger(text[: heads[0].start()], entries, newline)


def bullet(name: str, value: str, bold_colon: bool = True) -> str:
    head = f"- **{name}:** " if bold_colon else f"- **{name}** "
    return textwrap.fill(value, WIDTH, initial_indent=head, subsequent_indent="  ") + "\n"


def sub_bullets(head: str, items: list[str]) -> str:
    out = head + "\n"
    for item in items:
        out += textwrap.fill(item, WIDTH, initial_indent="  - ", subsequent_indent="    ") + "\n"
    return out


def render_open(key: str, at: str, actor: str) -> str:
    return f"## {key} · kind: open\n\n" + bullet("opened", f"{at} by {actor}")


RECEIPTS = ("guards", "read", "asked")


def render_close(key: str, rows: str, receipts: dict[str, str], summary: list[str], owed: list[str]) -> str:
    rec = [f"{k}: {receipts[k]}" for k in RECEIPTS if receipts.get(k)]
    return (
        f"## {key} · kind: close\n\n"
        + bullet("rows", rows)
        + sub_bullets("- **receipts:**", rec)
        + sub_bullets("- **summary** (the owner digest):", summary)
        + sub_bullets("- **Still owed:**", owed or ["nothing"])
    )


def render_pause(key: str, rows: str, deferred: str) -> str:
    return f"## {key} · kind: pause\n\n" + bullet("rows", rows) + bullet("deferred", deferred)


# -- banner -------------------------------------------------------------------------------


@dataclass
class Banner:
    key: str
    text: str  # the content under the heading, stripped of surrounding blank lines
    sha: str  # hash of heading and content, the `seen_hash` banner.set compares
    start: int  # heading start in the LF-normalised note
    end: int  # where the next `## ` heading starts


def read_banner(note: str) -> Banner:
    note = note.replace("\r\n", "\n")
    m = BANNER_RE.search(note)
    if not m:
        raise Refusal("the note has no `## Banner (<session key>)` heading", "add one: `## Banner (2026-10-08a)` followed by the banner text")
    nxt = re.search(r"^## ", note[m.end() :], re.MULTILINE)
    end = m.end() + nxt.start() if nxt else len(note)
    section = note[m.start() : end]
    sha = "sha256:" + hashlib.sha256(section.strip("\n").encode("utf-8")).hexdigest()[:16]
    return Banner(m.group("key"), note[m.end() : end].strip("\n"), sha, m.start(), end)


def replace_banner(note: str, key: str, text: str) -> str:
    if not SESSION_RE.match(key):
        raise Refusal(f"session key {key!r} is not like 2026-10-08a", "pass this session's key")
    newline = "\r\n" if note.count("\r\n") * 2 > note.count("\n") else "\n"
    norm = note.replace("\r\n", "\n")
    b = read_banner(norm)
    tail = norm[b.end :]
    out = norm[: b.start] + f"## Banner ({key})\n\n" + text.strip("\n") + "\n" + ("\n" if tail else "") + tail
    return out.replace("\n", newline) if newline != "\n" else out
