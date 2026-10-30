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
import subprocess
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


def _fill(text: str, first: str, rest: str) -> str:
    """Wrap at spaces only: a break inside `context-engine` or a long path hides it from a grep
    (CE-76, docs/evidence/adhoc-dryrun-2026-10-14.md F34); a word longer than a line overruns it."""
    return textwrap.fill(text, WIDTH, initial_indent=first, subsequent_indent=rest, break_on_hyphens=False, break_long_words=False) + "\n"


def bullet(name: str, value: str, bold_colon: bool = True) -> str:
    head = f"- **{name}:** " if bold_colon else f"- **{name}** "
    return _fill(value, head, "  ")


def sub_bullets(head: str, items: list[str]) -> str:
    out = head + "\n"
    for item in items:
        out += _fill(item, "  - ", "    ")
    return out


START_HEAD = "start head"  # HEAD when the session started: it reconciles foreign commits up to it (CE-65)


def _head(head: str | None) -> str:
    return bullet(START_HEAD, head) if head else ""


FOLLOWS = "follows"  # the closed session a follow-up continues (CE-84, DEC-45): `session start --follows <key>`; a bullet, not a digest line (DEC-106)


def _follows(key: str | None) -> str:
    return bullet(FOLLOWS, key) if key else ""


TASKS = "tasks"  # the board items the owner asked this session for, named at intake (`session tasks`, CE-112); the close's rows say how each ended


def _tasks(ids: str | None) -> str:
    return bullet(TASKS, ids) if ids else ""


def render_open(key: str, at: str, actor: str, head: str | None = None, follows: str | None = None) -> str:
    return f"## {key} · kind: open\n\n" + bullet("opened", f"{at} by {actor}") + _follows(follows) + _head(head)


RECEIPTS = ("guards", "read", "asked")


def render_close(key: str, rows: str, receipts: dict[str, str], summary: list[str], owed: list[str], head: str | None = None, follows: str | None = None, tasks: str | None = None) -> str:
    rec = [f"{k}: {receipts[k]}" for k in RECEIPTS if receipts.get(k)]
    return (
        f"## {key} · kind: close\n\n"
        + _follows(follows)
        + _tasks(tasks)
        + bullet("rows", rows)
        + sub_bullets("- **receipts:**", rec)
        + sub_bullets("- **summary** (the owner digest):", summary)
        + sub_bullets("- **Still owed:**", owed or ["nothing"])
        + _head(head)
    )


def render_pause(key: str, rows: str, deferred: str, head: str | None = None, follows: str | None = None, tasks: str | None = None) -> str:
    return f"## {key} · kind: pause\n\n" + _follows(follows) + _tasks(tasks) + bullet("rows", rows) + bullet("deferred", deferred) + _head(head)


def items(entry: Entry, head: str) -> list[str]:
    """The `  - ` items under the bullet that starts ``- **<head>`` (a close's `summary`, its
    `Still owed`), each with its continuation lines joined."""
    m = re.search(rf"^- \*\*{re.escape(head)}[^\n]*\n((?:  .*\n?)*)", entry.text, re.MULTILINE)
    out: list[str] = []
    for ln in (m.group(1).splitlines() if m else []):
        if ln.startswith("  - "):
            out.append(ln[4:].strip())
        elif out and ln.startswith("    "):
            out[-1] += " " + ln.strip()
    return out


# -- foreign commits (FRAMEWORK §6.10, CE-65) ----------------------------------------------

SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")


def _git(root, *args: str) -> str | None:
    """git's stdout, or None when git is missing or the command fails (no repo, no commits)."""
    try:
        p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    except OSError:
        return None
    return p.stdout if p.returncode == 0 else None


def head_sha(root) -> str | None:
    """HEAD's full hash, or None outside a git checkout or before its first commit."""
    out = _git(root, "rev-parse", "--verify", "-q", "HEAD")
    return out.strip() or None if out else None


def reconciled(led: Ledger) -> set[str]:
    """The hashes, as written, that a ``kind: foreign`` entry already names in its ``commits:``."""
    return {m for e in led.entries if e.kind == "foreign" for m in SHA_RE.findall(e.field("commits") or "")}


def _newest_in_history(root, heads: set[str]) -> str | None:
    """The one of ``heads`` nearest HEAD in HEAD's history; a hash no longer in it (rebased away,
    or gone from the object store) is dropped."""
    if heads:
        for sha in (_git(root, "rev-list", "HEAD") or "").split():
            if sha in heads:
                return sha
    return None


def foreign_baseline(root, led: Ledger, key: str | None, ledger_path: str) -> str | None:
    """The commit after which ``key`` looks for foreign commits (FRAMEWORK §6.10 item 2).

    `session start` records HEAD as the session's ``start head``, under the lock that mints its
    key, and a session reconciles the commits after the newest start head of a session keyed
    before it, up to and including its own start head (`foreign_range`). Those ranges partition
    HEAD's history: each foreign commit is exactly one session's, the first session whose start
    head it is at or before; except that a session's own start head rebased away, or a start head
    on a merged side branch, lets two ranges overlap (a double report, never a skip). A later key's start head is no baseline (that session may not have
    reconciled yet), and nor is "the newest commit touching the ledger that ``key`` did not
    make": another live session's milestone commits the ledger and moves that past foreign
    commits no session has reconciled (CE-65). Before any earlier entry records a start head,
    that older rule is the fallback, which can skip a commit once at the switch-over; None means
    the whole history."""
    heads = {e.field(START_HEAD) for e in led.entries if e.field(START_HEAD) and (key is None or key_order(e.key) < key_order(key))}
    base = _newest_in_history(root, heads)
    if base:
        return base
    args = ["log", "-1", "--format=%H"]
    if key:
        args += ["--invert-grep", f"--grep=Session: {key}"]
    out = _git(root, *args, "--", ledger_path)
    return out.strip() or None if out else None


def foreign_range(root, led: Ledger, key: str | None, ledger_path: str) -> tuple[str | None, str]:
    """``(baseline, end)``: ``key`` reconciles ``baseline..end``. ``end`` is its own start head,
    or HEAD when it recorded none (no key, a stub written before start heads, or a start head no
    longer in HEAD's history). A commit after the newest start head is the next session's."""
    own = led.get(key) if key else None
    end = _newest_in_history(root, {own.field(START_HEAD)}) if own and own.field(START_HEAD) else None
    return foreign_baseline(root, led, key, ledger_path), end or "HEAD"


def foreign_commits(root, led: Ledger, key: str | None, ledger_path: str) -> list[tuple[str, str, str]]:
    """``(hash, author, subject)`` of each commit in ``key``'s range (`foreign_range`) that carries
    no ``Session:`` line and that no ``kind: foreign`` entry names yet, oldest first. A ``Session:``
    line outside the trailer paragraph (an older layout) still makes the commit an agent's
    (procedures.md § Reconciling foreign commits)."""
    base, end = foreign_range(root, led, key, ledger_path)
    out = _git(root, "log", "--reverse", "--format=%H%x1f%an%x1f%s%x1f%B%x1e", f"{base}..{end}" if base else end)
    named = reconciled(led)
    found = []
    for rec in (out or "").split("\x1e"):
        parts = rec.strip("\n").split("\x1f")
        if len(parts) < 4:
            continue
        sha, author, subject, body = parts
        if re.search(r"^Session:", body, re.MULTILINE) or any(sha.startswith(n) for n in named):
            continue
        found.append((sha, author, subject))
    return found


# -- banner -------------------------------------------------------------------------------


@dataclass
class Banner:
    key: str
    text: str  # the content under the heading, stripped of surrounding blank lines
    sha: str  # hash of heading and content, the `seen_hash` banner.set compares
    start: int  # heading start in the LF-normalised note
    end: int  # where the next `## ` heading starts


NO_BANNER = "none"  # the `seen` hash of an orientation note with no banner yet: the first `banner set` passes it


def find_banner(note: str) -> Banner | None:
    """The orientation note's banner, or None when it has no ``## Banner (<key>)`` heading yet."""
    return read_banner(note) if BANNER_RE.search(note.replace("\r\n", "\n")) else None


def read_banner(note: str) -> Banner:
    note = note.replace("\r\n", "\n")
    m = BANNER_RE.search(note)
    if not m:
        raise Refusal("the orientation note has no `## Banner (<session key>)` heading", f"the first `banner set` writes it: pass --seen {NO_BANNER}")
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
    b = find_banner(norm)
    if b is None:  # the first banner goes before the orientation note's first `## ` section, so that section still bounds it
        first = re.search(r"^## ", norm, re.MULTILINE)
        start = end = first.start() if first else len(norm)
        if not first and norm and not norm.endswith("\n\n"):
            norm += "\n" if norm.endswith("\n") else "\n\n"
            start = end = len(norm)
    else:
        start, end = b.start, b.end
    tail = norm[end:]
    out = norm[:start] + f"## Banner ({key})\n\n" + text.strip("\n") + "\n" + ("\n" if tail else "") + tail
    return out.replace("\n", newline) if newline != "\n" else out
