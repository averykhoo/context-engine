"""Design reviews and the residual-risk register (FRAMEWORK P17, P18, §5.2, §7.4; CE-23).

A board item above the threshold carries ``review: [<trigger>, ...]`` (the triggers are
``[working] review_triggers``) and a ``## Design review`` section in this line format::

    affects: <who can be hurt>
    - eliminated: <risk>
    - reduced: <risk> | rung: <rung> | control: <guard or rule>
    - residual: <risk> | rung: <rung> | why: <why not eliminated> | control: <guard or rule>
    F: <forecast maintenance>
    A: <access for maintenance>
    M: <minimise interventions>
    E: <enable simple maintenance>

``task promote <id> NOW`` refuses while :func:`problems` finds anything, and ``task close``
appends every ``residual:`` line to the register: one markdown file of ``## INV-n: <risk>``
entries, appended idempotently (keyed on the task id and the risk text).

The engine's own register ships inside the package (:data:`PACKAGED`), so a repo the engine is
pointed at can read it (``register show --engine``): that is the handover (P17, regs. 7, 11).

Deliberately not here: deciding whether a task is above the threshold (its author declares it),
and turning the register into a record kind.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

SECTION = "Design review"
CLASSES = ("eliminated", "reduced", "residual")
RUNGS = ("eliminate", "reduce", "collective", "individual")  # P17's ladder, strongest first
FAME = ("F", "A", "M", "E")
RISK_KEYS = ("rung", "why", "control", "affects")
ENTRY_FIELDS = ("affects", "why not eliminated", "control", "from")
PACKAGED = "REGISTER.md"  # package data: the engine's own register, handed over with it
TEMPLATE = """affects: <who can be hurt: the building session, the next session, the owner, a plain-git human, every deployed repo>
- eliminated: <a risk the design cannot produce>
- reduced: <risk> | rung: <reduce|collective> | control: <the refusal, guard or rule, by name>
- residual: <risk> | rung: <reduce|collective|individual> | why: <why it was not eliminated> | control: <the guard or rule, by name>
F: <what will need doing to it later, by whom, how often, and what makes it stale>
A: <how it is read and fixed without the engine>
M: <which forms keep it from drifting>
E: <what it reuses: one name, one format, one runbook section>"""
HEADER = """# Residual-risk register

Residual risks (FRAMEWORK P17, §7.4): each is a risk that was not reasonably practicable to
eliminate, with whom it affects, why it stays, the control that holds it and where it came from.
`task close` appends the residuals of a task's `## Design review`; edit an entry only when the
code changes. Ids are `INV-n`, never reused.
"""

_RISK = re.compile(r"^- ([A-Za-z]+):\s*(.*)$")
_ENTRY = re.compile(r"^## (INV-(\d+)):[ \t]*(.*)$", re.MULTILINE)
_FIELD = re.compile(r"^- \*\*(.+?):\*\*[ \t]*(.*)$", re.MULTILINE)


@dataclass
class Risk:
    cls: str
    text: str
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class Review:
    affects: str | None = None
    risks: list[Risk] = field(default_factory=list)
    fame: dict[str, str] = field(default_factory=dict)
    bad: list[str] = field(default_factory=list)  # lines that do not parse

    @property
    def residuals(self) -> list[Risk]:
        return [r for r in self.risks if r.cls == "residual"]


def parse(section: str) -> Review:
    rv = Review()
    for raw in section.replace("\r\n", "\n").splitlines():
        line = raw.strip()
        if not line:
            continue
        if raw.startswith("- "):
            m = _RISK.match(raw)
            if not m:
                rv.bad.append(f"line {line[:60]!r} is not `- <class>: <risk>`")
                continue
            text, *parts = [p.strip() for p in m.group(2).split(" | ")]
            fields = {}
            for p in parts:
                k, sep, v = p.partition(":")
                if not sep:
                    rv.bad.append(f"field {p[:40]!r} in the {m.group(1)} line is not `key: value`")
                    continue
                fields[k.strip().lower()] = v.strip()
            rv.risks.append(Risk(m.group(1).lower(), text, fields))
            continue
        key, sep, value = line.partition(":")
        if sep and key.strip().lower() == "affects":
            rv.affects = value.strip()
        elif sep and key.strip() in FAME:
            rv.fame[key.strip()] = value.strip()
        elif not raw.startswith((" ", "\t")):  # an indented line continues the one above
            rv.bad.append(f"line {line[:60]!r} is not `affects:`, a `- <class>:` risk or an F/A/M/E line")
    return rv


def problems(rv: Review | None, section: str | None = None) -> list[str]:
    """Every reason the review is not ready, in reading order. Empty means valid."""
    if rv is None:
        return [f"there is no `## {SECTION}` section"]
    out = list(rv.bad)
    template = {ln.strip() for ln in TEMPLATE.splitlines()}
    if section is not None and any(ln.strip() in template for ln in section.splitlines()):
        out.append("the template's placeholder text is still there")
    if not rv.affects:
        out.append("no `affects:` line naming who can be hurt")
    if not rv.risks:
        out.append("no risk line (`- eliminated:`, `- reduced:` or `- residual:`)")
    for r in rv.risks:
        name = f"the {r.cls} risk {r.text[:40]!r}"
        if r.cls not in CLASSES:
            out.append(f"{name} has class {r.cls!r}, not one of {', '.join(CLASSES)}")
            continue
        if not r.text:
            out.append(f"a {r.cls} line names no risk")
        unknown = [k for k in r.fields if k not in RISK_KEYS]
        if unknown:
            out.append(f"{name} has unknown field {unknown[0]!r} (use {', '.join(RISK_KEYS)})")
        if r.cls in ("reduced", "residual"):
            rung = r.fields.get("rung")
            if rung not in RUNGS:
                out.append(f"{name} has no rung from the P17 ladder ({', '.join(RUNGS)})")
            elif r.cls == "residual" and rung == "eliminate":
                out.append(f"{name} is at rung eliminate, so it is not residual")
            elif r.cls == "reduced" and rung == "individual":
                out.append(f"{name} is held only at rung individual, so it is residual: write it as `- residual:` with `why:` (P17)")
        if r.cls == "residual":
            for k in ("why", "control"):
                if not r.fields.get(k):
                    out.append(f"{name} has no `{k}:`")
    for k in FAME:
        if not rv.fame.get(k):
            out.append(f"no `{k}:` line (F.A.M.E., P18)")
    return out


def read(body: str) -> tuple[Review | None, str | None]:
    """The parsed review of a record body, and the raw section (None, None when absent)."""
    from . import okf

    section = okf.get_section(body, SECTION)
    return (None, None) if section is None else (parse(section), section)


def check(body: str) -> tuple[Review | None, list[str]]:
    rv, section = read(body)
    return rv, problems(rv, section)


# -- the register ------------------------------------------------------------------------


@dataclass
class Entry:
    id: str
    n: int
    risk: str
    fields: dict[str, str]

    @property
    def source(self) -> str:
        """The task id in ``from:``, e.g. ``CE-3`` from ``CE-3, session 2026-10-12b``."""
        return self.fields.get("from", "").split(",")[0].strip()


def entries(text: str) -> list[Entry]:
    text = text.replace("\r\n", "\n")
    heads = list(_ENTRY.finditer(text))
    out = []
    for i, m in enumerate(heads):
        block = text[m.end() : heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        fields = {k.strip().lower(): v.strip() for k, v in _FIELD.findall(block)}
        out.append(Entry(m.group(1), int(m.group(2)), m.group(3).strip(), fields))
    return out


def key(source: str, risk: str) -> tuple[str, str]:
    return (source, " ".join(risk.split()))


def next_id(es: list[Entry], floor: int = 0) -> int:
    """One above the highest INV-n in the register and ``floor`` (the highest ever issued)."""
    return max([floor, *(e.n for e in es)]) + 1


def render(n: int, risk: Risk, affects: str, source: str, session: str) -> str:
    return (
        f"## INV-{n}: {risk.text}\n\n"
        f"- **affects:** {risk.fields.get('affects') or affects}\n"
        f"- **why not eliminated:** {risk.fields['why']}\n"
        f"- **control:** {risk.fields['rung']}: {risk.fields['control']}\n"
        f"- **from:** {source}, session {session}\n"
    )


def append(text: str | None, rv: Review, source: str, session: str, floor: int = 0) -> tuple[str, list[str]]:
    """The register text with every residual of ``rv`` not already in it, and the new ids.
    Idempotent: a residual already filed from ``source`` with the same risk text is skipped.
    New ids start above ``floor``, the highest id ever issued, so none is reused."""
    text = HEADER if text is None or not text.strip() else text.replace("\r\n", "\n")
    es = entries(text)
    have = {key(e.source, e.risk) for e in es}
    n = next_id(es, floor)
    added = []
    for r in rv.residuals:
        if key(source, r.text) in have:
            continue
        text = text.rstrip("\n") + "\n\n" + render(n, r, rv.affects or "", source, session)
        have.add(key(source, r.text))
        added.append(f"INV-{n}")
        n += 1
    return text, added


def entry_problems(es: list[Entry]) -> list[str]:
    out = []
    seen: set[str] = set()
    for e in es:
        if e.id in seen:
            out.append(f"{e.id} is used by two entries")
        seen.add(e.id)
        if not e.risk:
            out.append(f"{e.id} names no risk")
        for f in ENTRY_FIELDS:
            if not e.fields.get(f):
                out.append(f"{e.id} has no `{f}:` line")
    return out


def packaged() -> Path:
    """The register shipped with the engine (package data)."""
    return Path(str(resources.files("context_engine").joinpath(PACKAGED)))


def summary(text: str, where: str) -> str:
    es = entries(text)
    lines = [f"register {where}: {len(es)} residual risk{'s' if len(es) != 1 else ''}"]
    for e in es:
        lines.append(f"\n{e.id}: {e.risk}")
        lines += [f"  {f}: {e.fields[f]}" for f in ENTRY_FIELDS if e.fields.get(f)]
    return "\n".join(lines)
