"""Per-repo configuration: ``context.toml`` at the repo root (FRAMEWORK §8.0).

It names the record kinds, where each lives, its id series, its change mode and its schema.
The engine ships no record kinds of its own: a repo that has not declared a kind has none.
"""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath

from .errors import Refusal

CHANGE_MODES = ("append-only", "replaced", "stamped")
FIELD_TYPES = ("str", "date", "key", "list", "int")  # `key` is a session key, e.g. 2026-10-08c
CONFIG_NAME = "context.toml"
# Every guard id `context-engine lint` can report (FRAMEWORK §8.0 to §8.4); `[guards] off` may name only these.
LINT_IDS = (
    "schema", "G-D0", "G-D1", "G-D2", "G-D3", "G-D4", "G-D5", "G-D6", "G-D7", "G-D8", "G-D9", "G-D10", "G-D11", "G-D12", "G-R1",
    "G-I1", "G-I2", "G-T1", "G-T2", "G-T3", "G-T6",
    "G-W1", "G-W2", "G-W3", "G-W4", "G-W5", "G-W6", "G-W7", "G-W12", "G-W13",
)


@dataclass(frozen=True)
class Kind:
    name: str
    type: str  # the OKF `type:` value
    prefix: str  # id series, e.g. "DEC" for DEC-1, DEC-2, ...
    dir: str  # repo-relative directory holding the records
    mode: str  # one of CHANGE_MODES
    required: tuple[str, ...] = ()
    enums: dict[str, tuple[str, ...]] = field(default_factory=dict)
    extra_dirs: tuple[str, ...] = ()  # also scanned for ids, e.g. a legacy tasks/closed/
    types: dict[str, str] = field(default_factory=dict)  # field -> one of FIELD_TYPES

    @property
    def id_re(self) -> re.Pattern[str]:
        return re.compile(rf"^{re.escape(self.prefix)}-(\d+)$")


@dataclass(frozen=True)
class Working:
    """``[working]``: where the working state lives and which kinds play which part (FRAMEWORK §5)."""

    ledger: str = ""  # the session ledger, one markdown file (DEC-14: Q-H)
    handoff: str = ""  # the orientation note holding `## Banner (<key>)`
    board: tuple[str, ...] = ()  # kinds ranked on the board, e.g. ("task", "question")
    task: str = ""  # the kind `ask.answer` reports as unblocked and baton expiry files into
    question: str = ""
    decision: str = ""
    baton: str = ""
    pause: str = ""
    orient_max_bytes: int = 6000
    read_max_bytes: int = 6000  # every other MCP read (AC-19)
    caps: dict[str, int] = field(default_factory=lambda: {"NOW": 1, "NEXT": 5})
    ask_overdue_sessions: int = 5  # FRAMEWORK §5.3 (owner, 2026-10-07)
    ask_overdue_days: int = 7
    baton_max_age: int = 2  # sessions closed after the owning one (G-W3)
    max_pauses: int = 2  # consecutive `kind: pause` entries (G-W2, owner 2026-10-07)
    register: str = ""  # the residual-risk register, one markdown file (FRAMEWORK §7.4, CE-23)
    decision_index: str = ""  # the generated decision index, e.g. docs/decisions/index.md (FRAMEWORK §6.5, G-D6)
    review_triggers: tuple[str, ...] = ()  # the values a board item's `review:` may take (§5.2)
    criteria: str = ""  # the criteria file, one `| AC-n | ... |` table row per criterion; `decision link` checks criterion ids against it


@dataclass(frozen=True)
class Route:
    """``[[routes]]``: where one framework component lives and how it may change (FRAMEWORK §2)."""

    component: str
    path: str  # repo-relative file or directory; must exist (lint G-R1)
    mode: str  # free text: "replaced", "append-only: amend, never rewrite", ...
    pattern: str = ""  # how files under ``path`` are named, e.g. "US-n-<slug>.md"
    note: str = ""
    optional: bool = False  # may be absent, e.g. a gitignored directory on a fresh clone
    max_lines: int = 0  # G-D1 caps on the routed file, or on each .md under a routed directory; 0 is no cap
    max_bytes: int = 0
    max_width: int = 0  # characters per line; table rows are exempt


LIVENESS = ("LIVING", "ACTIVE-PLAN", "FROZEN")  # FRAMEWORK P2: whether a doc is kept current (its liveness)
# G-D5's counted nouns (FRAMEWORK P5): a number directly before one of these is a census of the tree.
# Plurals only: after a spelled number a singular is a modifier ("three entry points"). Measured
# 2026-10-13c (CE-33, docs/evidence/ce33-false-reds-2026-10-13.md): this list over this repo's
# docs flags 6 lines: 2 bounds (`at most 2 entries`, escaped), 1 in a doc now FROZEN, 2 real counts.
COUNT_NOUNS = (
    "tests", "checks", "guards", "criteria", "stories", "decisions", "tasks", "items", "rows", "questions",
    "records", "components", "rituals", "procedures", "goals", "runbooks", "kinds", "principles", "steps", "files",
    "entries", "ids", "scenarios",
)


# G-T2's default claim: a pytest marker `criterion("AC-n")`, or a comment `criterion: AC-n` in any language.
CLAIM = r"""criterion(?:\(\s*["']|:\s*)([A-Z]+-[1-9][0-9]*)"""


@dataclass(frozen=True)
class Guards:
    """``[guards]``: which guards lint reports and what the doc guards read (FRAMEWORK §8.0, §8.2,
    §8.3). A doc guard whose path list is empty checks nothing."""

    off: tuple[str, ...] = ()  # guard ids lint does not report (LINT_IDS)
    links: tuple[str, ...] = ()  # G-D3: files and directories whose links and `file::symbol` spans must resolve
    existence: tuple[str, ...] = ()  # G-T3: normative docs whose named files and `file::symbol` spans must exist
    signals: tuple[str, ...] = ()  # G-D7: files and directories under the signal budgets
    warn_max: int = 3  # G-D7: ⚠ per file
    bold_caps_max: int = 5  # G-D7: bold all-caps spans (`**NEVER**`) per file
    retired_glyphs: tuple[str, ...] = ()  # G-D7: glyphs no file may use any more
    coverage_spec: str = ""  # G-D12: the framework spec whose components, procedures and G-ids must be owned; unset (with coverage_maps) is off
    coverage_maps: str = ""  # G-D12: a repo-relative glob of dated coverage maps; the newest by the date and session letters in its file name is read
    charter: str = ""  # G-I1: the charter, whose table rows led by a goal id (`G-n`) are the goals a story's `goals` may name; unset is off
    stories: str = ""  # G-I1, G-I2, G-T1, G-T6: the record kind holding the stories; unset turns all four off
    tests: tuple[str, ...] = ()  # G-T2: files and directories whose claims trace tests and drivers to criteria; empty is off
    claim: str = CLAIM  # G-T2: a regex whose one group is the criterion id a test or driver claims
    liveness: tuple[str, ...] = ()  # G-D4: files and directories whose docs declare their liveness near the top; empty is off
    history: tuple[str, ...] = ()  # G-D4: directories of provenance, whose docs must be FROZEN, or ACTIVE-PLAN while their item is open
    liveness_given: dict[str, str] = field(default_factory=dict)  # G-D4: repo-relative glob -> liveness, for docs whose opening lines the repo may not edit
    liveness_lines: int = 10  # G-D4: how many lines from the top the declaration may sit (the window)
    numbers: tuple[str, ...] = ()  # G-D5: files and directories where a count of things in the tree may not be typed in prose; empty is off
    count_nouns: tuple[str, ...] = COUNT_NOUNS  # G-D5: the nouns a number counts when it stands directly before one


@dataclass(frozen=True)
class Config:
    kinds: dict[str, Kind]
    oplog: str = "docs/ledger/ops.jsonl"
    lockfile: str = ".context/engine.lock"
    bundles: tuple[str, ...] = ()
    lock_timeout: float = 30.0
    contract: str = "CLAUDE.md"  # the file holding `framework: <major.minor>` (lint G-D0, DEC-23)
    commit: str = "milestones"  # when the engine commits its writes by path (FRAMEWORK §5.5 rule 4, DEC-36): one of COMMIT_POLICIES
    working: Working = field(default_factory=Working)
    routes: tuple[Route, ...] = ()
    guards: Guards = field(default_factory=Guards)

    def kind_for_id(self, record_id: str) -> Kind:
        for k in self.kinds.values():
            if k.id_re.match(record_id):
                return k
        raise Refusal(
            f"no record kind has ids like {record_id!r}",
            f"use an id from a configured series ({', '.join(k.prefix + '-n' for k in self.kinds.values())}); an old id (an alias) is looked up by `task show`, `decision show` and `why`",
        )

    def kind(self, name: str) -> Kind:
        try:
            return self.kinds[name]
        except KeyError:
            raise Refusal(
                f"no record kind named {name!r}",
                f"use one of {', '.join(sorted(self.kinds))}, or declare it in {CONFIG_NAME}",
            ) from None


def _known(table: str, got: dict, allowed) -> None:
    """Refuse a key the engine does not read, so a typo fails rather than becoming a silent default."""
    extra = sorted(set(got) - set(allowed))
    if extra:
        raise Refusal(f"{table} has unknown key {extra[0]!r}", f"use only {', '.join(allowed)} (the kit's context.toml.template is the schema)")


def _typed(table: str, got: dict, spec: dict[str, type | tuple[type, ...]]) -> None:
    """Refuse a value of the wrong TOML type, so `orient_max_bytes = "big"` fails too."""
    for key, want in spec.items():
        if key not in got:
            continue
        v = got[key]
        ok = isinstance(v, want) and not (isinstance(v, bool) and bool not in (want if isinstance(want, tuple) else (want,)))
        if ok and want is list:
            ok = all(isinstance(x, str) for x in v)
        if not ok:
            names = " or ".join(t.__name__ for t in (want if isinstance(want, tuple) else (want,)))
            raise Refusal(f"{table} `{key}` is {type(v).__name__} {v!r}, not {names}", "fix its type (the kit's context.toml.template shows each)")


TOP_KEYS = ("engine", "kinds", "working", "routes", "guards")
ENGINE_KEYS = ("oplog", "lockfile", "bundles", "lock_timeout", "contract", "commit")
ENGINE_TYPES = {"oplog": str, "lockfile": str, "bundles": list, "lock_timeout": (int, float), "contract": str, "commit": (str, bool)}
# FRAMEWORK §5.5 rule 4 (DEC-36): commit at milestones (task close, owner words, batons and pauses,
# session close or pause, the banner), after every write, or never but a pause. A bool is CE-45's spelling,
# which init wrote into every repo as `commit = true`: true is the engine committing, now at
# milestones, and false is off.
COMMIT_POLICIES = ("milestones", "every-write", "off")
COMMIT_BOOLS = {True: "milestones", False: "off"}
KIND_KEYS = tuple(f for f in Kind.__dataclass_fields__ if f != "name")
KIND_TYPES = {"type": str, "prefix": str, "dir": str, "mode": str, "required": list, "enums": dict, "extra_dirs": list, "types": dict}
_PY = {str: str, int: int, tuple: list, dict: dict}
WORKING_TYPES = {f: _PY[type(getattr(Working(), f))] for f in Working.__dataclass_fields__}
ROUTE_TYPES = {f: (bool if f == "optional" else int if f.startswith("max_") else str) for f in Route.__dataclass_fields__}
GUARDS_TYPES = {f: _PY[type(getattr(Guards(), f))] for f in Guards.__dataclass_fields__}


def from_dict(raw: dict) -> Config:
    _known("the top level", raw, TOP_KEYS)
    engine = raw.get("engine", {})
    _known("[engine]", engine, ENGINE_KEYS)
    _typed("[engine]", engine, ENGINE_TYPES)
    kinds = {}
    prefixes = set()
    for name, k in raw.get("kinds", {}).items():
        _known(f"[kinds.{name}]", k, KIND_KEYS)
        _typed(f"[kinds.{name}]", k, KIND_TYPES)
        mode = k.get("mode")
        if mode not in CHANGE_MODES:
            raise Refusal(
                f"kind {name!r} has mode {mode!r}",
                f"set `mode` to one of {', '.join(CHANGE_MODES)} in [kinds.{name}]",
            )
        for key in ("type", "prefix", "dir"):
            if not k.get(key):
                raise Refusal(f"kind {name!r} has no `{key}`", f"add `{key} = ...` to [kinds.{name}]")
        if k["prefix"] in prefixes:
            raise Refusal(f"two kinds share the id prefix {k['prefix']!r}", "give each kind its own prefix")
        prefixes.add(k["prefix"])
        types = dict(k.get("types", {}))
        bad = {f: t for f, t in types.items() if t not in FIELD_TYPES}
        if bad:
            f, t = next(iter(bad.items()))
            raise Refusal(f"kind {name!r} gives field {f!r} type {t!r}", f"use one of {', '.join(FIELD_TYPES)}")
        kinds[name] = Kind(
            name=name,
            type=k["type"],
            prefix=k["prefix"],
            dir=k["dir"],
            mode=mode,
            required=tuple(k.get("required", ())),
            enums={f: tuple(v) for f, v in k.get("enums", {}).items()},
            extra_dirs=tuple(k.get("extra_dirs", ())),
            types=types,
        )
    w = raw.get("working", {})
    _known("[working]", w, Working.__dataclass_fields__)
    _typed("[working]", w, WORKING_TYPES)
    named = [w[r] for r in ("task", "question", "decision", "baton", "pause") if w.get(r)] + list(w.get("board", ()))
    for name in named:
        if name not in kinds:
            raise Refusal(f"[working] names kind {name!r}, which is not declared", f"declare [kinds.{name}] or fix [working]")
    if w.get("decision_index") and not w.get("decision"):
        raise Refusal("[working] sets `decision_index` but names no `decision` kind", "set `decision = \"<kind>\"` in [working], or drop `decision_index`")
    caps = w.get("caps", {})
    tiers = sorted({p for n in w.get("board", ()) for p in kinds[n].enums.get("pri", ())})
    if tiers:  # a cap names a board tier, so a typo (`NEXTT`) fails rather than leaving a tier uncapped
        _known("[working.caps]", caps, tiers)
    _typed("[working.caps]", caps, {t: int for t in caps})
    working = Working(
        **{k: (tuple(v) if k in ("board", "review_triggers") else v) for k, v in w.items() if k in Working.__dataclass_fields__ and k != "caps"},
        caps={**Working().caps, **w.get("caps", {})},
    )
    routes = []
    for n, r in enumerate(raw.get("routes", ()), 1):
        for key in ("component", "path", "mode"):
            if not r.get(key):
                raise Refusal(f"route {n} has no `{key}`", f"add `{key} = ...` to the {n}th [[routes]] entry")
        extra = set(r) - set(Route.__dataclass_fields__)
        if extra:
            raise Refusal(f"route {n} has unknown key {sorted(extra)[0]!r}", f"use only {', '.join(Route.__dataclass_fields__)}")
        _typed(f"route {n}", r, ROUTE_TYPES)
        routes.append(Route(**r))
    g = raw.get("guards", {})
    _known("[guards]", g, Guards.__dataclass_fields__)
    _typed("[guards]", g, GUARDS_TYPES)
    unknown = [x for x in g.get("off", ()) if x not in LINT_IDS]
    if unknown:
        raise Refusal(f"[guards] `off` names {unknown[0]!r}, which lint does not report", f"use guard ids lint reports: {', '.join(LINT_IDS)}")
    if g.get("stories") and g["stories"] not in kinds:
        raise Refusal(f"[guards] `stories` names kind {g['stories']!r}, which is not declared", f"name the stories' kind ({', '.join(sorted(kinds))}), or unset it")
    try:
        groups = re.compile(g.get("claim", CLAIM)).groups
    except re.error as err:
        raise Refusal(f"[guards] `claim` is not a regular expression ({err})", "fix the pattern; its one group is the claimed criterion id") from None
    if groups != 1:
        raise Refusal(f"[guards] `claim` has {groups} groups", "give it exactly one group, the claimed criterion id (make others `(?:...)`)")
    for glob, word in g.get("liveness_given", {}).items():
        if word not in LIVENESS:
            raise Refusal(f"[guards] `liveness_given` gives {glob!r} the liveness {word!r}", f"give one of {', '.join(LIVENESS)}")
        if not glob or PureWindowsPath(glob).anchor or ".." in PureWindowsPath(glob).parts:  # `/` and `\` alike, as G-D12's glob
            raise Refusal(f"[guards] `liveness_given` names {glob!r}, which is not a glob relative to the repo root", "name the docs from the repo root, with no `..` and no leading `/` or drive")
    if "liveness_lines" in g and g["liveness_lines"] < 1:
        raise Refusal(f"[guards] `liveness_lines` is {g['liveness_lines']}", "give the window at least 1 line (the engine default is 10)")
    nouns = g.get("count_nouns", COUNT_NOUNS)
    bad = [n for n in nouns if not isinstance(n, str) or not re.fullmatch(r"[A-Za-z][A-Za-z-]*", n)]
    if not nouns or bad:
        raise Refusal(f"[guards] `count_nouns` {'is empty' if not nouns else f'holds {bad[0]!r}, which is not a word'}", "list the plural nouns a typed count may name (`tests`, `checks`, ...); to switch G-D5 off, empty `numbers` instead")
    guards = Guards(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in g.items()})
    commit = engine.get("commit", Config.commit)
    commit = COMMIT_BOOLS.get(commit, commit) if isinstance(commit, bool) else commit
    if commit not in COMMIT_POLICIES:
        raise Refusal(f"[engine] `commit` is {commit!r}", f"set it to one of {', '.join(map(json.dumps, COMMIT_POLICIES))} (FRAMEWORK §5.5 rule 4)")
    return Config(
        kinds=kinds,
        oplog=engine.get("oplog", Config.oplog),
        lockfile=engine.get("lockfile", Config.lockfile),
        bundles=tuple(engine.get("bundles", ())),
        lock_timeout=float(engine.get("lock_timeout", Config.lock_timeout)),
        contract=engine.get("contract", Config.contract),
        commit=commit,
        working=working,
        routes=tuple(routes),
        guards=guards,
    )


def load(root: Path) -> Config:
    path = Path(root) / CONFIG_NAME
    if not path.exists():
        raise Refusal(f"no {CONFIG_NAME} at {root}", f"create {CONFIG_NAME} declaring the repo's record kinds")
    return from_dict(tomllib.loads(path.read_text(encoding="utf-8-sig")))  # an editor's BOM is not a config error
