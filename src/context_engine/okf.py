"""OKF markdown records: frontmatter read with ruamel, written surgically.

A record is ``---\\n<yaml>\\n---\\n<body>``. Reading parses the frontmatter with ruamel's
round-trip loader. Writing never re-dumps the whole frontmatter: ruamel does not reproduce flow
mappings byte for byte (``{ by: x }`` comes back as ``{by: x}``), so only the keys an operation
changes are re-serialised and every other line is kept verbatim (AC-1, AC-2).

Line endings: the document is handled with ``\\n`` inside and written back with the line ending
it was read with, because a Windows checkout with ``core.autocrlf`` holds CRLF files.

Deliberately not handled: nested edits (a write replaces a whole top-level key), and files that
mix CRLF and LF (they are written back with the dominant ending).
"""

from __future__ import annotations

import hashlib
import io
import re
from dataclasses import dataclass, field
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from .errors import Refusal

AMENDMENTS_HEADING = re.compile(r"^## Amendments[ \t]*$", re.MULTILINE)


def _yaml() -> YAML:
    y = YAML()  # round-trip mode: keeps comments, key order and quoting on read
    y.preserve_quotes = True
    y.width = 4096  # never fold a long title onto a second line
    return y


@dataclass
class Document:
    """One parsed record. ``fm_lines`` excludes the ``---`` fences; each line ends in ``\\n``."""

    fm_lines: list[str] | None  # None: the file has no frontmatter at all
    body: str
    newline: str
    raw: str | None = None  # the exact text read, kept while the document is unmodified
    data: CommentedMap = field(default_factory=CommentedMap)

    @property
    def dirty(self) -> bool:
        return self.raw is None

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    # -- frontmatter edits -------------------------------------------------------------

    def _spans(self) -> dict[str, tuple[int, int]]:
        """Line span [start, end) of each top-level key, excluding trailing blank/comment lines."""
        keys = list(self.data.keys())
        starts = [self.data.lc.key(k)[0] for k in keys]
        spans = {}
        for i, k in enumerate(keys):
            end = starts[i + 1] if i + 1 < len(keys) else len(self.fm_lines)
            while end - 1 > starts[i] and _is_filler(self.fm_lines[end - 1]):
                end -= 1
            spans[k] = (starts[i], end)
        return spans

    def set(self, key: str, value: Any) -> None:
        """Set one top-level key, keeping every other line verbatim."""
        if self.fm_lines is None:
            self.fm_lines = []
        spans = self._spans()
        if key in spans:
            start, end = spans[key]
            new = dump_key(key, value)
            eol = _eol_comment(self.data, key, self.fm_lines[start])
            if eol and len(new) == 1 and end - start == 1:
                new = [new[0].rstrip("\n") + eol + "\n"]
            self.fm_lines[start:end] = new
        else:
            self.fm_lines.extend(dump_key(key, value))
        self._reparse()

    def delete(self, key: str) -> None:
        if self.fm_lines is None:
            return
        spans = self._spans()
        if key in spans:
            start, end = spans[key]
            del self.fm_lines[start:end]
            self._reparse()

    def set_body(self, body: str) -> None:
        self.body = body
        self.raw = None

    def _reparse(self) -> None:
        self.data = _load("".join(self.fm_lines))
        self.raw = None

    # -- output ------------------------------------------------------------------------

    def render(self) -> str:
        if self.raw is not None:
            return self.raw
        if self.fm_lines is None:
            text = self.body
        else:
            text = "---\n" + "".join(self.fm_lines) + "---\n" + self.body
        return text.replace("\n", self.newline) if self.newline != "\n" else text


def _is_filler(line: str) -> bool:
    s = line.strip()
    return not s or s.startswith("#")


def _eol_comment(data: CommentedMap, key: str, line: str) -> str:
    """The end-of-line comment on a key's line with the spaces before it, e.g. ``   # pending``.

    Taken from the original line: ruamel's comment token drops the spaces in front of it."""
    item = data.ca.items.get(key)
    if not item or len(item) < 3 or item[2] is None:
        return ""
    col = item[2].start_mark.column
    line = line.rstrip("\n")
    if col >= len(line) or line[col] != "#":
        return ""
    lead = len(line[:col]) - len(line[:col].rstrip())
    return line[col - lead :] if lead else " " + line[col:]


def _load(text: str) -> CommentedMap:
    try:
        data = _yaml().load(text) if text.strip() else CommentedMap()
    except Exception as exc:  # ruamel raises several unrelated types
        raise Refusal(
            f"frontmatter is not valid YAML ({type(exc).__name__}: {str(exc).splitlines()[0]})",
            "quote any value that contains ': ' or starts with a YAML indicator, then retry",
        ) from exc
    if not isinstance(data, CommentedMap):
        raise Refusal("frontmatter is not a mapping", "make the frontmatter `key: value` lines")
    return data


def dump_key(key: str, value: Any) -> list[str]:
    """Serialise one top-level ``key: value``. Lists and maps of scalars come out in flow style."""
    if isinstance(value, (list, tuple)):
        seq = CommentedSeq(value)
        seq.fa.set_flow_style()
        value = seq
    elif isinstance(value, dict) and not isinstance(value, CommentedMap):
        m = CommentedMap(value)
        m.fa.set_flow_style()
        value = m
    out = io.StringIO()
    _yaml().dump({key: value}, out)
    text = out.getvalue()
    if value is None:  # ruamel writes `key:` with a trailing space on some versions
        text = f"{key}:\n"
    return text.splitlines(keepends=True)


def parse(text: str) -> Document:
    """Parse a record. Text without a frontmatter fence parses with empty frontmatter."""
    newline = "\r\n" if text.count("\r\n") * 2 > text.count("\n") else "\n"
    norm = text.replace("\r\n", "\n")
    if not norm.startswith("---\n"):
        return Document(fm_lines=None, body=norm, newline=newline, raw=text)
    end = norm.find("\n---\n", 3)
    if end == -1:
        if norm.endswith("\n---"):
            end = len(norm) - 4
        else:
            raise Refusal("frontmatter has no closing `---` line", "add a `---` line after the last key")
    fm = norm[4 : end + 1]
    body = norm[end + 5 :]
    return Document(
        fm_lines=fm.splitlines(keepends=True), body=body, newline=newline, raw=text, data=_load(fm)
    )


def read_head(path) -> Document:
    """Parse only a record's frontmatter: the file is read up to its closing fence, never further.

    Listing reads every record, so it must not pay for (or choke on) bodies (AC-13)."""
    lines: list[bytes] = []
    with open(path, "rb") as f:
        if f.readline().rstrip(b"\r\n") != b"---":
            return Document(fm_lines=None, body="", newline="\n")
        for line in f:
            if line.rstrip(b"\r\n") == b"---":
                break
            lines.append(line)
        else:
            raise Refusal(f"{path} has no closing `---` line", "add a `---` line after the last key")
    fm = b"".join(lines).decode("utf-8").replace("\r\n", "\n")
    return Document(fm_lines=fm.splitlines(keepends=True), body="", newline="\n", data=_load(fm))


def has_frontmatter(doc: Document) -> bool:
    return doc.fm_lines is not None


def new_document(fields: dict[str, Any], body: str, newline: str = "\n") -> Document:
    lines: list[str] = []
    for k, v in fields.items():
        lines.extend(dump_key(k, v))
    body = "\n" + body.strip("\n") + "\n" if body.strip() else ""
    doc = Document(fm_lines=lines, body=body, newline=newline, raw=None)
    doc.data = _load("".join(lines))
    return doc


# -- append-only bodies (G-D10) -----------------------------------------------------------


def original_body(body: str) -> str:
    """The part of a body that may never change: everything above ``## Amendments``."""
    norm = body.replace("\r\n", "\n")
    m = AMENDMENTS_HEADING.search(norm)
    return norm[: m.start()] if m else norm


def body_sha(body: str) -> str:
    """Hash of the original body, independent of line endings and surrounding blank lines (AC-7)."""
    canon = original_body(body).strip("\n") + "\n"
    return "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest()


# -- body sections (replaced-mode records) ------------------------------------------------


def _section_span(body: str, name: str) -> tuple[int, int] | None:
    """[start, end) of the content under ``## name``; the end is the next ``## `` heading."""
    m = re.search(rf"^## {re.escape(name)}[ \t]*(?:\n|\Z)", body, re.MULTILINE)  # the whole heading: `Log` is not `Logs`
    if not m:
        return None
    nxt = re.search(r"^## ", body[m.end() :], re.MULTILINE)
    return m.end(), m.end() + nxt.start() if nxt else len(body)


def get_section(body: str, name: str) -> str | None:
    span = _section_span(body.replace("\r\n", "\n"), name)
    return None if span is None else body.replace("\r\n", "\n")[span[0] : span[1]].strip("\n")


def set_section(body: str, name: str, text: str) -> str:
    """Replace the content of ``## name``, appending the section if it is missing."""
    text = text.strip("\n")
    span = _section_span(body, name)
    if span is None:
        return body.rstrip("\n") + f"\n\n## {name}\n\n{text}\n"
    start, end = span
    tail = body[end:]
    return body[:start] + "\n" + text + "\n" + ("\n" if tail else "") + tail


def append_to_section(body: str, name: str, line: str) -> str:
    """Append one line at the end of ``## name``, creating the section if needed."""
    current = get_section(body, name)
    return set_section(body, name, (current + "\n" if current else "") + line)
