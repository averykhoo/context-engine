"""CE-165 sabotage table (DEC-11): break what each pinned test guards; every NEW run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce165.py [--base <rev>]`. Unlike
tools/sabotage_ce42.py it never edits the shared tree (docs/runbooks/sabotage.md, Traps): it makes
two git worktrees in a temp directory, NEW (HEAD plus this tree's uncommitted changes to tracked
files) and OLD (``--base``, default 2d211ba: the commit before CE-165's pins), breaks each case's
files in the worktree, and runs pytest there with PYTHONPATH=<worktree>/src (the env's editable
install imports the main tree's src, which would give a false green). Each run gets a fresh
bytecode cache (PYTHONPYCACHEPREFIX): a same-length break written in the same second as the
previous restore would otherwise run the stale .pyc (seen 2026-10-08d).

Each case is (what, [(file, exact old text, new text), ...], NEW selector, OLD selector or None).
The NEW run must be RED. The OLD run, where given, shows what the test before CE-165 said under
the same break: GREEN there is the verifier's finding the pin closes. A pattern that does not
match exactly once stops the script (the code moved); a run that selects no test counts as green.
Both worktrees are removed at the end.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
GU, WK, BS = "src/context_engine/guards.py", "src/context_engine/working.py", "src/context_engine/bootstrap.py"
CM, CF = "src/context_engine/commit.py", "src/context_engine/config.py"
TG, TC, TW = "tests/test_guards.py", "tests/test_coverage_status.py", "tests/test_working.py"
TK, TCM, TR = "tests/test_kit.py", "tests/test_commit.py", "tests/test_reserve.py"
G_D4 = f"{TG}::test_g_d4_an_expired_stale_after_on_a_live_record_criterion_or_register_entry_is_red"
STORES = f"{TC}::test_coverage_prints_the_totals_the_rules_and_a_table_per_class_and_stores_nothing"
FOLLOW = f"{TW} -k refuses_to_follow_a_session_that_is_not_closed"
ROSTER = "tests/test_roster.py -k roster_keeps_fable"
MCP = f"{TK} -k mcp_connect_timeout"
RECEIPT = f"{TW} -k guards_receipt_without_a_gate_result"
LOCKED = "lock():\n            raw = self._utf8(p, rel)\n"

CASES = [
    # B1 AC-150
    ("B1a stale() no longer skips a deprecated record", [(GU, 'doc.get("status") == "deprecated" or ', "")], G_D4, G_D4),
    ("B1b stale() no longer skips a closed record", [(GU, ' or str(doc.get("state")) in DONE_STATES', "")], G_D4, G_D4),
    # B2 AC-160
    ("B2a criterion_new reads and writes without the lock",
     [(WK, "with self.store." + LOCKED + "            place = CR.target(raw, under)", "if True:\n            raw = self._utf8(p, rel)\n            place = CR.target(raw, under)")],
     "tests/test_criteria_write.py -k holding_the_repo_lock", "tests/test_criteria_write.py"),
    ("B2b criterion_set reads and writes without the lock",
     [(WK, "with self.store." + LOCKED + "            found = CR.rows_of(raw, cid)", "if True:\n            raw = self._utf8(p, rel)\n            found = CR.rows_of(raw, cid)")],
     "tests/test_criteria_write.py -k holding_the_repo_lock", "tests/test_criteria_write.py"),
    # B3a
    ("B3a coverage appends to the newest map",
     [(GU, "    return newest.relative_to(e.root).as_posix(), result\n", '    newest.write_bytes(newest.read_bytes() + b"x")\n    return newest.relative_to(e.root).as_posix(), result\n')],
     STORES, STORES),
    # B3b AC-171
    ("B3b coverage ignores G-D12's own failures",
     [(GU, "    if out:\n        f = out[0]\n        raise Refusal(f\"G-D12 cannot read its sources", "    if False:\n        f = out[0]\n        raise Refusal(f\"G-D12 cannot read its sources")],
     f"{TC} -k \"each_g_d12_map_failure or says_why_g_d12\"", None),
    ("B3b coverage gives one generic reason",
     [(GU, 'raise Refusal(f"G-D12 cannot read its sources: {f.path}: {f.message}", f.remedy)', 'raise Refusal("G-D12 cannot read its sources", f.remedy)')],
     f"{TC} -k \"each_g_d12_map_failure or says_why_g_d12\"", None),
    # B4 AC-123
    ("B4a an abandoned session is followable", [(WK, 'if entry.kind != "close":', 'if entry.kind not in ("close", "abandoned"):')], FOLLOW, FOLLOW),
    ("B4b the abandoned remedy dropped", [(WK, '                "abandoned": "its unfinished work is in the baton it was abandoned with: do that baton",\n', "")], FOLLOW, FOLLOW),
    ("B4c the open remedy reworded", [(WK, "work in it if it is yours, or wait for its close", "work in it if it is yours")], FOLLOW, FOLLOW),
    ("B4d the missing-key remedy reworded", [(WK, '"pass the key of a closed session, as its', '"pass a closed session\'s key, as its')], FOLLOW, FOLLOW),
    # B5 AC-113
    ("B5 the housekeeping Writes cell widened",
     [("docs/framework/FRAMEWORK.md", "| only through `hk_` operations, each logged as mechanical |", "| only through `hk_` operations, and by hand where they fall short |")],
     ROSTER, ROSTER),
    # B6 bootstrap.py::APPENDED
    ("B6a .gitattributes dropped from APPENDED", [(BS, "APPENDED = (CONTRACT_TARGET, REPO_IGNORE, REPO_ATTRIBUTES)", "APPENDED = (CONTRACT_TARGET, REPO_IGNORE)")],
     f"{TK} -k gitattributes_stays_hard_linked", f"{TK} -k gitattributes"),
    ("B6b .gitignore dropped from APPENDED", [(BS, "APPENDED = (CONTRACT_TARGET, REPO_IGNORE, REPO_ATTRIBUTES)", "APPENDED = (CONTRACT_TARGET, REPO_ATTRIBUTES)")],
     f"{TK} -k gitignore_stays_hard_linked", f"{TK} -k gitignore"),
    # B7 AC-115
    ("B7a G-D0's contract compare reads the kit's bytes",
     [(WK, 'want_text = (K.KIT / K.CONTRACT).read_text(encoding="utf-8").replace("\\r\\n", "\\n")', 'want_text = (K.KIT / K.CONTRACT).read_bytes().decode("utf-8")')],
     f"{TK} -k crlf_checkout_lints", f"{TK} -k line_endings_change_nothing"),
    ("B7b the kit block is read as bytes, line endings kept",
     [(BS, 'block = kit_block((KIT / BOOTLOADER).read_text(encoding="utf-8"))', 'block = kit_block((KIT / BOOTLOADER).read_bytes().decode("utf-8"))'),
      (BS, '    norm = text.replace("\\r\\n", "\\n")\n    m = ANY_BEGIN.search(norm)', "    norm = text\n    m = ANY_BEGIN.search(norm)")],
     f"{TK} -k crlf_checkout_lints", f"{TK} -k line_endings_change_nothing"),
    # B8 (CE-161 already split the layers' texts): a confirming sabotage, no new code
    ("B8 the op's lint layer reads no failure",
     [(WK, "bad = [f for f in self.lint() if f.path in carried or f.path.startswith(dirs)]", "bad = []")],
     f"{TCM}::test_a_sweep_never_commits_a_record_whose_frontmatter_does_not_parse", f"{TCM}::test_a_sweep_never_commits_a_record_whose_frontmatter_does_not_parse"),
    # B9
    ("B9a an empty path counts as a path", [(CM, 'out = [str(o["path"])] if o.get("path") else []', 'out = [str(o["path"])] if "path" in o else []')],
     f"{TCM} -k \"select_never_takes or never_carries_another_sessions_id_reserve\"", f"{TCM} {TR}"),
    ("B9b select takes every id.reserve line",
     [(CM, "(taken if own(o, k, ln) or carried(ps) else left)", '(taken if own(o, k, ln) or carried(ps) or (o or {}).get("op") == "id.reserve" else left)')],
     f"{TCM} -k \"select_never_takes or never_carries_another_sessions_id_reserve\"", f"{TCM} {TR}"),
    ("B9c ask new drops the given id",
     [(WK, 'brief=brief, body=text, extra=extra, rid=rid)', 'brief=brief, body=text, extra=extra, rid="")')],
     f"{TR} -k ask_new_takes", TR),
    # B10 AC-110 (kit text)
    ("B10a the remedy's MCP_TIMEOUT misspelled (the example kept)",
     [("src/context_engine/kit/README.md", "`MCP_TIMEOUT` (milliseconds)", "`MCP_TIMOUT` (milliseconds)")], MCP, MCP),
    ("B10b the unit dropped", [("src/context_engine/kit/README.md", "`MCP_TIMEOUT` (milliseconds) in", "`MCP_TIMEOUT` in")], MCP, MCP),
    ("B10c the example in seconds", [("src/context_engine/kit/README.md", "`MCP_TIMEOUT=180000`", "`MCP_TIMEOUT=180`")], MCP, MCP),
    # B11 AC-149
    ("B11 doc archive names pointers with G-D3 off",
     [(WK, '        if "G-D3" in self.store.config.guards.off:\n            return []\n        return [(f.path, f.message) for f in G.links(self)]', "        return [(f.path, f.message) for f in G.links(self)]")],
     "tests/test_docs.py -k pointers_when_g_d3_is_off", None),
    # B12 INV-86 (DEC-288)
    ("B12a GATE_RECEIPT loosened back to any `not run`",
     [(CF, '|^\\s*not run\\b|\\bgate\\b[^;,.]*?\\bnot run\\b"', '|not run"')], RECEIPT, None),
    ("B12b GATE_RECEIPT's opening anchor dropped", [(CF, '|^\\s*not run\\b|', '|not run\\b|')], RECEIPT, None),
    ("B12c the template's pattern left loose (an existing pin: AC-32's template==default)",
     [("src/context_engine/kit/context.toml.template", "|^\\s*not run\\b|\\bgate\\b[^;,.]*?\\bnot run\\b'", "|not run'")],
     f"{TK} -k config_template_names_every_key", None),
]


def git(*args, cwd=ROOT):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def run(tree, sel):
    env = {**os.environ, "PYTHONPATH": os.path.join(tree, "src"), "PYTHONPYCACHEPREFIX": tempfile.mkdtemp()}
    env.pop("CE_SESSION", None)
    p = subprocess.run(f'"{PY}" -m pytest -q -p no:cacheprovider {sel}', cwd=tree, env=env, capture_output=True, text=True, shell=True)
    last = (p.stdout.strip().splitlines() or ["?"])[-1]
    failed = sorted({ln.split("::")[-1].split(" ")[0] for ln in p.stdout.splitlines() if ln.startswith("FAILED")})
    return ("RED" if "failed" in last or " error" in last else "GREEN"), last, failed


def broken(tree, edits):
    saved = {}
    for rel, old, new in edits:
        path = os.path.join(tree, rel)
        text = saved.get(rel) or open(path, encoding="utf-8", newline="").read()
        saved.setdefault(rel, text)
        cur = open(path, encoding="utf-8", newline="").read()
        assert cur.count(old) == 1, (tree, rel, old)
        open(path, "w", encoding="utf-8", newline="").write(cur.replace(old, new))
    return saved


def restore(tree, saved):
    for rel, text in saved.items():
        open(os.path.join(tree, rel), "w", encoding="utf-8", newline="").write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="2d211ba")
    ap.add_argument("-k", default="", help="run only the cases whose name contains this")
    args = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="ce165-")
    new, old = os.path.join(tmp, "new"), os.path.join(tmp, "old")
    git("worktree", "add", "--detach", new, "HEAD")
    git("worktree", "add", "--detach", old, args.base)
    results = []
    try:
        for rel in git("diff", "--name-only", "HEAD").split():
            shutil.copyfile(os.path.join(ROOT, rel), os.path.join(new, rel))
        for what, edits, sel_new, sel_old in CASES:
            if args.k not in what:
                continue
            saved = broken(new, edits)
            try:
                got_new = run(new, sel_new)
            finally:
                restore(new, saved)
            got_old = None
            if sel_old:
                saved = broken(old, edits)
                try:
                    got_old = run(old, sel_old)
                finally:
                    restore(old, saved)
            results.append((what, got_new, got_old))
            print(f"{got_new[0]:5} new | {got_old[0] if got_old else 'n/a':5} old | {what} | {got_new[1]} | {', '.join(got_new[2])}", flush=True)
        clean = run(new, "tests/test_guards.py tests/test_coverage_status.py tests/test_working.py tests/test_roster.py tests/test_kit.py tests/test_commit.py tests/test_reserve.py tests/test_docs.py tests/test_criteria_write.py")
        print(f"restored NEW tree, the touched files' tests: {clean[0]} | {clean[1]}")
        for rel in git("diff", "--name-only", "HEAD").split():
            assert open(os.path.join(new, rel), "rb").read() == open(os.path.join(ROOT, rel), "rb").read(), rel
        assert git("status", "--porcelain", cwd=old).strip() == "", "the OLD tree is restored"
    finally:
        git("worktree", "remove", "--force", new)
        git("worktree", "remove", "--force", old)
        shutil.rmtree(tmp, ignore_errors=True)
    ok = all(n[0] == "RED" for _, n, _ in results) and clean[0] == "GREEN"
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
