"""Per-repo configuration: ``context.toml`` at the repo root (FRAMEWORK §8.0).

It names the record kinds, where each lives, its id series, its change mode and its schema.
The engine ships no record kinds of its own: a repo that has not declared a kind has none.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .errors import Refusal

CHANGE_MODES = ("append-only", "replaced", "stamped")
CONFIG_NAME = "context.toml"


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

    @property
    def id_re(self) -> re.Pattern[str]:
        return re.compile(rf"^{re.escape(self.prefix)}-(\d+)$")


@dataclass(frozen=True)
class Config:
    kinds: dict[str, Kind]
    oplog: str = "docs/ledger/ops.jsonl"
    lockfile: str = ".context/engine.lock"
    bundles: tuple[str, ...] = ()
    lock_timeout: float = 30.0

    def kind_for_id(self, record_id: str) -> Kind:
        for k in self.kinds.values():
            if k.id_re.match(record_id):
                return k
        raise Refusal(
            f"no record kind has ids like {record_id!r}",
            f"use an id from a configured series ({', '.join(k.prefix + '-n' for k in self.kinds.values())})",
        )

    def kind(self, name: str) -> Kind:
        try:
            return self.kinds[name]
        except KeyError:
            raise Refusal(
                f"no record kind named {name!r}",
                f"use one of {', '.join(sorted(self.kinds))}, or declare it in {CONFIG_NAME}",
            ) from None


def from_dict(raw: dict) -> Config:
    engine = raw.get("engine", {})
    kinds = {}
    prefixes = set()
    for name, k in raw.get("kinds", {}).items():
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
        kinds[name] = Kind(
            name=name,
            type=k["type"],
            prefix=k["prefix"],
            dir=k["dir"],
            mode=mode,
            required=tuple(k.get("required", ())),
            enums={f: tuple(v) for f, v in k.get("enums", {}).items()},
            extra_dirs=tuple(k.get("extra_dirs", ())),
        )
    return Config(
        kinds=kinds,
        oplog=engine.get("oplog", Config.oplog),
        lockfile=engine.get("lockfile", Config.lockfile),
        bundles=tuple(engine.get("bundles", ())),
        lock_timeout=float(engine.get("lock_timeout", Config.lock_timeout)),
    )


def load(root: Path) -> Config:
    path = Path(root) / CONFIG_NAME
    if not path.exists():
        raise Refusal(f"no {CONFIG_NAME} at {root}", f"create {CONFIG_NAME} declaring the repo's record kinds")
    return from_dict(tomllib.loads(path.read_text(encoding="utf-8")))
