"""Freezing and archiving docs (CE-27, FRAMEWORK §6.7, §7.2, §7.3): `doc freeze` writes the
FROZEN line G-D4 reads, `task close` refuses to leave an ACTIVE-PLAN doc behind it, and `doc
archive` moves a committed doc unrepaired, first line `ARCHIVED <date>`, with a row in its
directory's one redirect table, which the next commit carries as a rename."""

import copy
import dataclasses
import datetime as dt
import json

import pytest

from context_engine import archive as A
from context_engine import guards as G
from context_engine import ops
from context_engine.cli import main
from context_engine.config import load
from context_engine.errors import Refusal
from context_engine.working import Engine

from conftest import _toml
from test_commit import _init, git
from test_working import ACTOR, CONFIG, FRAMEWORK, LEDGER, NOTE, TODAY

DOCS = copy.deepcopy(CONFIG)
DOCS["guards"] = {"off": ["G-D9"], "liveness": ["docs"], "history": ["evidence"]}
DOCS["working"]["archive"] = "docs/archive"
KEY = "2026-10-08a"  # what `session start` mints from LEDGER on TODAY
W = {"session": KEY, "actor": ACTOR}
PLAN = "evidence/plan-2026-10-08.md"
OLD = "# Old notes\n\nLIVING. Kept current until it grew past its cap.\n\n" + "".join(f"- fact {n}: something learned\n" for n in range(12))


def target(root, config=DOCS) -> Engine:
    root.mkdir(parents=True, exist_ok=True)
    (root / "context.toml").write_text(_toml(config), encoding="utf-8")
    (root / "ledger.md").write_text(LEDGER, encoding="utf-8")
    (root / "HANDOFF.md").write_text(NOTE.format(key="2026-10-07b"), encoding="utf-8")
    (root / "CLAUDE.md").write_text(f"# contract\n\nframework: {FRAMEWORK}\n", encoding="utf-8")
    write(root, "docs/a.md", "# A\n\nLIVING. A doc G-D4 reads.\n")
    write(root, "evidence/run-2026-10-07.md", "# Run\n\nFROZEN 2026-10-07b. As measured.\n")
    return Engine(root, today=lambda: TODAY)


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))


def reds(e: Engine) -> list[str]:
    return [f"{f.path}: {f.message}" for f in e.lint() if f.guard == "G-D4"]


def snapshot(root) -> dict:
    """Every file's bytes, but git's and the engine lock's."""
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and not {".git", ".context"} & set(p.relative_to(root).parts)}


def oplines(root) -> list[dict]:
    return [json.loads(x) for x in (root / "ops.jsonl").read_text(encoding="utf-8").splitlines()]


# -- doc freeze -------------------------------------------------------------------------------


@pytest.mark.criterion("AC-81")
def test_freeze_writes_the_frozen_line_g_d4_reads_above_the_plan_and_changes_nothing_else(tmp_path):
    e = target(tmp_path)
    t = e.new("task", "build it", **W)
    before = f"\ufeff# Plan\r\n\r\nACTIVE-PLAN for {t.id}: what is left.\r\n\r\n- step one\r\n"  # a BOM and CRLF stay
    write(tmp_path, PLAN, before)
    assert reds(e) == []
    out = e.doc_freeze(PLAN, **W)
    assert out == f"{PLAN}: FROZEN 2026-10-08 written on line 3, above its ACTIVE-PLAN line; G-D4 now reads it as FROZEN"
    stamp = f"FROZEN 2026-10-08 (session {KEY}): {t.id} closed; below, the plan as it stood"
    assert (tmp_path / PLAN).read_bytes().decode("utf-8") == before.replace("ACTIVE-PLAN", f"{stamp}\r\n\r\nACTIVE-PLAN", 1)
    assert oplines(tmp_path)[-1] | {"at": None} == {"at": None, "session": KEY, "actor": ACTOR, "op": "doc.freeze", "id": PLAN, "path": PLAN, "fields": ["liveness"], "mechanical": False}
    e.close(t.id, "done", **W)  # the freeze lets the close through, and G-D4 stays green
    assert reds(e) == []
    # a declaration on the first line, a note of its own, wrapped at A.WRAP; the doc's LF kept
    write(tmp_path, "docs/b.md", "LIVING. Kept current.\nSecond line.\n")
    note = "retired: " + "superseded by the new runbook " * 5
    e.doc_freeze("docs/b.md", note=note, **W)
    text = (tmp_path / "docs/b.md").read_text(encoding="utf-8")
    head, rest = text.split("\n\n", 1)
    assert rest == "LIVING. Kept current.\nSecond line.\n" and "\r" not in text
    assert head.startswith(f"FROZEN 2026-10-08 (session {KEY}): retired: superseded") and max(map(len, head.split("\n"))) <= A.WRAP < len(head)
    assert G.declared(text, 10).word == "FROZEN" and reds(e) == []
    # the CLI runs the same operation
    write(tmp_path, "docs/c.md", "# C\n\nACTIVE-PLAN until the trial ends.\n")
    assert main(["--root", str(tmp_path), "--actor", ACTOR, "--session", KEY, "doc", "freeze", "docs/c.md", "--note", "the trial ended"]) == 0
    assert f"\n\nFROZEN {dt.date.today().isoformat()} (session {KEY}): the trial ended\n\nACTIVE-PLAN" in (tmp_path / "docs/c.md").read_text(encoding="utf-8")  # the CLI's clock is real


@pytest.mark.criterion("AC-81")
def test_freeze_refuses_what_it_cannot_freeze_and_writes_nothing(tmp_path):
    e = target(tmp_path, {**DOCS, "guards": {**DOCS["guards"], "liveness_given": {"docs/given.md": "LIVING"}}})
    t = e.new("task", "build it", **W)
    write(tmp_path, "docs/frozen.md", "# F\n\nFROZEN 2026-10-01. As measured.\n")
    write(tmp_path, "docs/none.md", "# N\n\nNo declaration here.\n")
    write(tmp_path, "docs/fm.md", "---\ntype: Runbook\nliveness: LIVING\n---\n\n# R\n")
    write(tmp_path, "docs/given.md", "# G\n\nKept by another tool.\n")
    write(tmp_path, "docs/notes.txt", "LIVING.\n")
    cases = {
        "docs/frozen.md": "docs/frozen.md is already FROZEN (line 3)",
        "docs/none.md": "docs/none.md declares no liveness in its first 10 lines",
        "docs/fm.md": "docs/fm.md declares LIVING in its frontmatter",
        "docs/given.md": "docs/given.md's liveness is given in config",
        "docs/notes.txt": "docs/notes.txt is not a markdown doc",
        "docs/gone.md": "there is no file 'docs/gone.md'",
        "../outside.md": "../outside.md is outside this repo's root",
        t.path.relative_to(tmp_path).as_posix(): f"{t.path.relative_to(tmp_path).as_posix()} is a task record, not a doc",
    }
    before = snapshot(tmp_path)
    for path, says in cases.items():
        with pytest.raises(Refusal) as r:
            e.doc_freeze(path, **W)
        assert r.value.message.startswith(says), (path, r.value.message)
    assert snapshot(tmp_path) == before


# -- task close and the ACTIVE-PLAN docs naming it --------------------------------------------


@pytest.mark.criterion("AC-82")
def test_close_refuses_the_last_open_item_an_active_plan_names_until_it_is_frozen(tmp_path):
    e = target(tmp_path)
    t = e.new("task", "first half", **W)
    u = e.new("task", "second half", **W)
    write(tmp_path, PLAN, f"# Plan\n\nACTIVE-PLAN for {t.id} and {u.id}.\n")
    write(tmp_path, "docs/design.md", f"> **ACTIVE-PLAN** while {u.id} is open.\n")
    e.close(t.id, "half done", **W)  # the plan still serves an open item
    with pytest.raises(Refusal) as r:
        e.close(u.id, "all done", **W)
    assert r.value.message.startswith(f"{u.id} is the last open item that ACTIVE-PLAN docs docs/design.md, {PLAN} name, so closing it would turn G-D4 red")
    assert r.value.remedy.startswith(f"freeze each first: `doc freeze docs/design.md`; `doc freeze {PLAN}`; then close {u.id} again")
    assert e.store.get(u.id).doc.get("state") == "open" and reds(e) == []  # refused before any byte
    e.doc_freeze("docs/design.md", **W)
    with pytest.raises(Refusal, match=f"ACTIVE-PLAN doc {PLAN} names"):
        e.close(u.id, "all done", **W)
    e.doc_freeze(PLAN, **W)
    e.close(u.id, "all done", **W)
    assert reds(e) == []
    # with G-D4 off nothing reads the plan, so nothing refuses
    off = target(tmp_path / "off", {**DOCS, "guards": {**DOCS["guards"], "off": ["G-D9", "G-D4"]}})
    v = off.new("task", "alone", **W)
    write(tmp_path / "off", PLAN, f"# Plan\n\nACTIVE-PLAN for {v.id}.\n")
    off.close(v.id, "done", **W)


# -- doc archive ------------------------------------------------------------------------------


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    target(root)
    write(root, "docs/old.md", OLD)
    write(root, "docs/b.md", "# B\n\nFROZEN 2026-10-01. A measurement.\n\n" + "".join(f"- row {n}\n" for n in range(12)))
    write(root, "docs/fm.md", "---\ntitle: x\n---\n\nLIVING.\n")
    write(root, "docs/README.md", "# Docs\n\nLIVING.\n")
    write(root, "docs/sub/old.md", OLD)
    _init(root)
    return root


def archive(root, path, config=None, **kw):
    """`doc archive` as the CLI and MCP run it (`Op.call`), dated TODAY."""
    o = ops.OPS["doc_archive"]
    return o.call(Engine(root, config=config, today=lambda: TODAY), ops.Caller(KEY, ACTOR), path=path, **kw)[1]


@pytest.mark.criterion("AC-83")
def test_archive_moves_a_committed_doc_unrepaired_with_its_archived_line_and_a_redirect_row(repo):
    out = archive(repo, "docs/old.md", why="over its cap (G-D1)")
    assert out == "docs/old.md: archived as docs/archive/old.md (first line ARCHIVED 2026-10-08), row added to docs/archive/README.md"
    assert not (repo / "docs/old.md").exists()
    assert (repo / "docs/archive/old.md").read_text(encoding="utf-8") == f"ARCHIVED 2026-10-08 (session {KEY}), from docs/old.md.\n\n{OLD}"
    row = f"| docs/old.md | [old.md](old.md) | 2026-10-08 (session {KEY}) | over its cap (G-D1) |"
    assert (repo / "docs/archive/README.md").read_text(encoding="utf-8") == A.redirects(None, "docs/archive", row)
    assert G.declared((repo / "docs/archive/README.md").read_text(encoding="utf-8"), 10).word == "LIVING"
    assert [(x["op"], x["path"], x["fields"]) for x in oplines(repo)[-3:]] == [
        ("doc.archive", "docs/old.md", ["moved"]), ("doc.archive", "docs/archive/old.md", ["archived"]), ("doc.archive", "docs/archive/README.md", ["redirect"])]
    assert reds(Engine(repo)) == []  # the ARCHIVED line reads as FROZEN, the table as LIVING
    # not a milestone (DEC-36): nothing staged; the next commit carries the move, and git sees a rename
    assert git(repo, "diff", "--cached", "--name-only") == "" and git(repo, "log", "-1", "--format=%s").strip() == "base"
    ops.OPS["commit"].call(Engine(repo), ops.Caller(KEY, ACTOR), message="CE-1: archive the old notes")
    assert git(repo, "status", "--porcelain=v1", "--untracked-files=all") == ""
    moved = git(repo, "show", "-M", "--name-status", "--format=", "HEAD").splitlines()
    assert any(ln.startswith("R") and ln.endswith("\tdocs/old.md\tdocs/archive/old.md") for ln in moved), moved
    # a second archive adds its row under the first
    archive(repo, "docs/b.md", to="docs/archive")
    rows = [ln for ln in (repo / "docs/archive/README.md").read_text(encoding="utf-8").splitlines() if ln.startswith("| docs/")]
    assert rows == [row, f"| docs/b.md | [b.md](b.md) | 2026-10-08 (session {KEY}) | — |"]


@pytest.mark.criterion("AC-83")
def test_archive_refuses_what_it_cannot_move_unrepaired_and_writes_nothing(repo):
    write(repo, "docs/new.md", "# New\n\nLIVING.\n")
    write(repo, "docs/edited.md", "# E\n\nLIVING.\n")
    git(repo, "add", "docs/edited.md")
    git(repo, "commit", "-q", "-m", "edited")
    write(repo, "docs/edited.md", "# E\n\nLIVING. Changed.\n")
    archive(repo, "docs/sub/old.md")  # takes the name docs/archive/old.md first
    (repo / "docs/latin").mkdir()
    (repo / "docs/latin/README.md").write_bytes("# Archiv\n\nGelöscht.\n".encode("latin-1"))  # a redirect table not in UTF-8
    write(repo, "decisions/DEC-1.md", "# A decision\n\nLIVING.\n")
    cfg = load(repo)
    bare = dataclasses.replace(cfg, working=dataclasses.replace(cfg.working, archive=""))
    cases = [
        ("docs/new.md", {}, "docs/new.md is not tracked by git"),
        ("docs/edited.md", {}, "docs/edited.md has uncommitted changes"),
        ("docs/fm.md", {}, "docs/fm.md opens with frontmatter"),
        ("docs/old.md", {}, "docs/archive/old.md exists already"),
        ("docs/archive/old.md", {}, "docs/archive/old.md is already in the archive directory docs/archive"),
        ("docs/README.md", {}, "docs/README.md has the name of an archive's redirect table"),
        ("docs/b.md", {"to": "../elsewhere"}, "../elsewhere is outside this repo's root"),
        ("docs/b.md", {"config": bare}, "no archive directory given, and [working] has no `archive`"),
        ("docs/b.md", {"to": "."}, "the archive directory is the repo root"),
        ("docs/b.md", {"to": "decisions"}, "decisions holds decision records"),
        ("decisions/DEC-1.md", {}, "decisions/DEC-1.md is a decision record, not a doc"),
        ("docs/b.md", {"to": "docs/latin"}, "docs/latin/README.md is not UTF-8"),  # read before the first write
    ]
    status, files = git(repo, "status", "--porcelain=v1", "--untracked-files=all"), snapshot(repo)
    for path, kw, says in cases:
        with pytest.raises(Refusal) as r:
            archive(repo, path, **kw)
        assert r.value.message.startswith(says), (path, r.value.message)
    assert git(repo, "status", "--porcelain=v1", "--untracked-files=all") == status
    assert snapshot(repo) == files


@pytest.mark.criterion("AC-83")
def test_archive_names_a_config_entry_left_pointing_at_the_old_path(tmp_path):
    root = tmp_path / "repo"
    target(root, {**DOCS, "guards": {**DOCS["guards"], "liveness": ["docs", "docs/old.md"]}})
    write(root, "docs/old.md", OLD)
    _init(root)
    out = archive(root, "docs/old.md")
    assert "; context.toml still names docs/old.md: point it at docs/archive/old.md or drop it, or lint is red (G-R1, G-D4)" in out
    assert reds(Engine(root)) == ["context.toml: [guards] liveness names docs/old.md, which does not exist"]


def test_the_redirect_table_takes_a_row_in_a_readme_written_by_hand_keeping_its_bytes():
    row = "| a.md | [a.md](a.md) | 2026-10-08 (session 2026-10-08a) | why |"
    hand = "# Archive\r\n\r\nNothing here is kept current."  # CRLF, no final newline, no table
    assert A.redirects(hand, "docs/archive", row) == hand + "\r\n\r\n## Redirects\r\n\r\n" + "\r\n".join([A.REDIRECT_HEAD, A.REDIRECT_RULE, row]) + "\r\n"
    table = f"# Archive\n\n{A.REDIRECT_HEAD}\n{A.REDIRECT_RULE}\n| x.md | [x.md](x.md) | 2026-10-01 | — |\n\nA note after the table.\n"
    assert A.redirects(table, "docs/archive", row) == table.replace("— |\n", f"— |\n{row}\n")
    last = f"{A.REDIRECT_HEAD}\n{A.REDIRECT_RULE}\n| x.md | [x.md](x.md) | 2026-10-01 | — |"  # the table ends the file, with no newline
    assert A.redirects(last, "d", row) == f"{last}\n{row}\n"
    assert A.redirect_row("a b|c.md", "a b|c.md", "2026-10-08", "2026-10-08a", "") == "| a b\\|c.md | [a b\\|c.md](a%20b%7Cc.md) | 2026-10-08 (session 2026-10-08a) | — |"
