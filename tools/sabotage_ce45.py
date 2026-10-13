"""CE-45 sabotage table (DEC-11): break what each test of the engine's own commit guards (FRAMEWORK
§5.5 rule 4: the op log is committed with every write); every run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce45.py [row-number ...]` (no numbers: every
row). It restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13c; when the code moves, a pattern stops matching and the script stops with an
AssertionError naming it, rather than passing quietly. G-T5 (mutation per criterion) replaces this
hand table.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a same-length sabotage written in the
same second as the previous restore would otherwise run the stale .pyc (seen 2026-10-08d).
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
CM = "src/context_engine/commit.py"
ST = "src/context_engine/store.py"
OP = "src/context_engine/ops.py"
MC = "src/context_engine/mcp.py"
WK = "src/context_engine/working.py"
T = "tests/test_commit.py"
S = [
 # the defect itself: no commit after a write, so a by-path task commit leaves the op log behind
 (ST, "                if self._batch == 0:\n                    self._commit()", "                pass", T + " -k library_call"),
 (CM, "    if not _in_git_tree(root):\n        return Outcome()", "    return Outcome()\n    if not _in_git_tree(root):\n        return Outcome()", T + " -k mid_session"),
 # what rides along: a commit of the index as well takes another session's staged edit
 # (dropping `--only` alone is no sabotage: paths after `--` imply it)
 (CM, '"commit", "-q", "--only", "-F"', '"commit", "-q", "--include", "-F"', T + " -k nothing_else"),
 # the sweep: only the op log, not the files its lines name
 (CM, 'wanted = list(dict.fromkeys([oplog, *(str(o["path"]) for o in ops if o.get("path"))]))', "wanted = [oplog]", T + " -k mid_session"),
 # the sweep: only this session's own lines' files, so a leftover record stays behind
 (CM, 'for o in ops if o.get("path"))]))', 'for o in ops if o.get("path") and o.get("session") == session)]))', T + " -k leftover"),
 # the leftover is named in the message
 (CM, '    if others:\n', '    if False:\n', T + " -k leftover"),
 # the trailer
 (CM, 'return f"{title}\\n\\n{body}Session: {session}\\n"', 'return f"{title}\\n\\n{body}"', T + " -k nothing_else"),
 # in-progress states
 (CM, "        if (gitdir / name).exists():", "        if False:", T + " -k in_progress"),
 (CM, '        if (gitdir / name).exists():\n            return Outcome(note=f"{what} is in progress', '        if (gitdir / name).exists() and False:\n            return Outcome(note=f"{what} is in progress', T + " -k real_merge"),
 (CM, '    if git.run("symbolic-ref", "-q", "HEAD").returncode != 0:', "    if False:", T + " -k detached"),
 # hooks are never bypassed
 (CM, '"commit", "-q", "--only", "-F"', '"commit", "-q", "--no-verify", "--only", "-F"', T + " -k hooks_run"),
 # git's index.lock is waited for
 (CM, "LOCK_RETRIES = 10", "LOCK_RETRIES = 1", T + " -k index_lock"),
 # an ignored op log keeps the repo's choice
 (CM, "    if oplog not in paths:\n        return Outcome()", "    if False:\n        return Outcome()", T + " -k ignored_op_log"),
 # a root below the top of the work tree
 (CM, "        code = codes.get(prefix + rel)", "        code = codes.get(rel)", T + " -k below_the_top"),
 # untracked files need an add before --only
 (CM, "    if untracked:\n", "    if False:\n", T + " -k nothing_else"),
 # line endings in the op log
 (CM, "have = Counter(ln for ln in head.splitlines() if ln.strip())", 'have = Counter(ln for ln in head.split("\\n") if ln.strip())', T + " -k multiset"),
 (CM, "        if have[ln]:\n            have[ln] -= 1", "        if have[ln]:\n            pass", T + " -k multiset"),
 # the title cap
 (CM, "            if len(title) + len(sep) + len(p) + (len(more) if n < len(parts) - 1 else 0) > TITLE_MAX:", "            if False:", T + " -k title_stays"),
 # one operation, one commit; the CLI and MCP path
 (OP, "        with store.batch():\n            code, text = self.fn(target, c, **kw)", "        if True:\n            code, text = self.fn(target, c, **kw)", T + " -k writes_twice"),
 (OP, "        return code, text + store.last_commit.line()", "        return code, text", T + " -k mcp_tool"),
 (MC, "            _, text = o.call(e, c, **kw)", "            _, text = o.fn(e, c, **kw)", T + " -k mcp_tool"),
 # the off switch, and the pause that commits regardless (AC-14)
 (ST, "        if not (self.config.commit or always):", "        if not self.config.commit:", T + " -k commit_false"),
 (ST, "        if not (self.config.commit or always):", "        if not always:", T + " -k commit_false or nothing_else"),
 (WK, "            self.store.commit_always = True\n", "", T + " -k commit_false"),
 # a non-git target says nothing
 (CM, "    if not _in_git_tree(root):\n        return Outcome()", "    if not _in_git_tree(root):\n        return Outcome(note='no git')", T + " -k not_a_git_repo"),
]
only = {int(a) for a in sys.argv[1:]}
ok = True
for n, (f, old, new, sel) in enumerate(S, 1):
    if only and n not in only:
        continue
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8").replace("\r\n", "\n")  # a CRLF checkout (autocrlf) matches too
    assert text.count(old) == 1, (n, f, old[:60], text.count(old))
    try:
        broken = text.replace(old, new)
        p.write_bytes((broken.replace("\n", "\r\n") if b"\r\n" in orig else broken).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        why = [l.strip()[:110] for l in r.stdout.splitlines() if l.startswith("E ")][:1]
        red = r.returncode == 1 and "failed" in "".join(last)  # a test failed: not a collection error, not "no tests ran"
        ok &= red
        print(f"{n:2} {'RED ' if red else 'GREEN!'} {f.rsplit('/', 1)[-1]:12} {old.strip().splitlines()[0][:50]!r:54} -> {last} {why}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
